from typing import List, Optional
import torch
from torch import nn
import opt_einsum as oe

# Helper to compute product - avoid asyncio issues by using pure Python
def _prod(xs):
    """Compute product of a list of numbers"""
    if len(xs) == 0:
        return 1
    result = 1
    for x in xs:
        result *= int(x)
    return result


def _contract_cores(cores) -> torch.Tensor:
    """Contract cores (r_{k-1}, m_k, n_k, r_k) into a (m1..md, n1..nd) tensor."""
    d = len(cores)
    letters = 'abcdefghijklmnopqrstuvwxyz'
    # d+1 rank indices + d out-mode indices + d in-mode indices must be distinct
    if 3 * d + 1 > len(letters):
        raise ValueError(f"TT depth d={d} too large for einsum alphabet (max {(len(letters) - 1) // 3})")
    ranks, outs, ins = letters[:d + 1], letters[d + 1:2 * d + 1], letters[2 * d + 1:3 * d + 1]
    terms = [f"{ranks[k]}{outs[k]}{ins[k]}{ranks[k + 1]}" for k in range(d)]
    return oe.contract(','.join(terms) + '->' + outs + ins, *cores)


class TTLinear(nn.Module):
    """
    Tensor-Train Linear layer:
    - Stores cores G_k with shape (r_{k-1}, m_k, n_k, r_k)
    - Forward reconstructs full W via einsum, then y = x @ W^T + b
    - Supports use_dense_path for debugging (reconstructs full weight)
    """
    
    def __init__(
        self, 
        in_modes: List[int], 
        out_modes: List[int], 
        ranks: List[int], 
        bias: bool = True,
        use_dense_path: bool = False
    ):
        super().__init__()
        assert len(in_modes) == len(out_modes), "in_modes and out_modes must have same length"
        d = len(in_modes)
        assert len(ranks) == d + 1, f"ranks must be length d+1 with r0=rd=1, got {len(ranks)} for d={d}"
        assert ranks[0] == 1 and ranks[-1] == 1, f"r0 and rd must be 1, got r0={ranks[0]}, rd={ranks[-1]}"
        
        self.in_modes = list(in_modes)
        self.out_modes = list(out_modes)
        self.ranks = list(ranks)
        self.in_features = _prod(in_modes)
        self.out_features = _prod(out_modes)
        self.use_dense_path = use_dense_path

        cores = []
        for k in range(d):
            G = torch.empty(self.ranks[k], self.out_modes[k], self.in_modes[k], self.ranks[k+1])
            # Xavier-like init scaled by ranks
            nn.init.xavier_uniform_(G.view(self.ranks[k], -1))
            cores.append(nn.Parameter(G))
        self.cores = nn.ParameterList(cores)
        self.bias = nn.Parameter(torch.zeros(self.out_features)) if bias else None

    def reconstruct_weight(self) -> torch.Tensor:
        """
        Contract cores into a big (m1,...,md, n1,...,nd) tensor T, then reshape to (M, N)
        Build einsum string with unique indices for each mode
        """
        T = _contract_cores(list(self.cores))  # shape (m1,...,md, n1,...,nd)
        W = T.reshape(self.out_features, self.in_features)
        return W

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass: x @ W^T + b
        x: (B, in_features)
        """
        # Cache reconstruction for efficiency (can be optimized further)
        if not hasattr(self, '_cached_weight') or self._cached_weight is None:
            W = self.reconstruct_weight()  # (out_features, in_features)
            if not self.training:  # Cache in eval mode
                self._cached_weight = W
        else:
            W = self._cached_weight
        
        y = x.matmul(W.t())
        
        if self.bias is not None:
            y = y + self.bias
        return y
    
    def train(self, mode: bool = True):
        """Override train to clear cache"""
        super().train(mode)
        if mode:  # Clear cache when entering training mode
            if hasattr(self, '_cached_weight'):
                self._cached_weight = None
        return self

    def copy_from_dense(self, weight: torch.Tensor, bias: Optional[torch.Tensor] = None):
        """Init cores by TT-SVD of a dense weight of shape (out_features, in_features)."""
        cores = tt_svd_init_from_dense(weight.detach(), self.in_modes, self.out_modes, self.ranks)
        with torch.no_grad():
            for core, c in zip(self.cores, cores):
                core.copy_(c)
            if bias is not None and self.bias is not None:
                self.bias.copy_(bias)
        self._cached_weight = None

def tt_tensor(W: torch.Tensor, out_modes: List[int], in_modes: List[int]) -> torch.Tensor:
    """(M, N) matrix -> interleaved (m1, n1, ..., md, nd) tensor, so each TT core owns (m_k, n_k).

    Its k-th unfolding (first k pairs as rows) is the matrix TT-SVD truncates at step k.
    """
    d = len(in_modes)
    return W.reshape(*out_modes, *in_modes).permute(*[i for k in range(d) for i in (k, d + k)])


def tt_svd_init_from_dense(
    W: torch.Tensor, 
    in_modes: List[int], 
    out_modes: List[int], 
    ranks: List[int]
) -> List[torch.Tensor]:
    """
    Initialize TT cores from a dense weight matrix using TT-SVD decomposition.
    
    Args:
        W: Dense weight matrix of shape (out_features, in_features)
        in_modes: List of input mode dimensions
        out_modes: List of output mode dimensions
        ranks: List of TT ranks [r0, r1, ..., rd] where r0=rd=1
    
    Returns:
        List of TT cores
    """
    d = len(in_modes)
    assert len(out_modes) == d, "in_modes and out_modes must have same length"
    assert len(ranks) == d + 1 and ranks[0] == 1 and ranks[-1] == 1, \
        f"ranks must be length d+1 with r0=rd=1, got {ranks}"
    assert W.shape == (_prod(out_modes), _prod(in_modes)), \
        f"W shape {tuple(W.shape)} doesn't match ({_prod(out_modes)}, {_prod(in_modes)})"

    rest = tt_tensor(W, out_modes, in_modes)
    cores = []
    for k in range(d - 1):
        mat = rest.reshape(ranks[k] * out_modes[k] * in_modes[k], -1)
        U, S, Vh = torch.linalg.svd(mat, full_matrices=False)
        r = min(ranks[k + 1], S.numel())
        # Zero-pad when the requested rank exceeds the unfolding's rank, so core shapes match TTLinear
        core = W.new_zeros(mat.shape[0], ranks[k + 1])
        core[:, :r] = U[:, :r]
        cores.append(core.reshape(ranks[k], out_modes[k], in_modes[k], ranks[k + 1]))
        rest = W.new_zeros(ranks[k + 1], Vh.shape[1])
        rest[:r] = S[:r, None] * Vh[:r]
    cores.append(rest.reshape(ranks[d - 1], out_modes[-1], in_modes[-1], 1))
    return cores


class TTEmbedding(nn.Module):
    """
    TT factorization for embeddings: vocab x dim -> TT cores (modes for vocab, dim).
    """
    
    def __init__(
        self, 
        in_modes: List[int], 
        out_modes: List[int], 
        ranks: List[int],
        use_dense_path: bool = False
    ):
        super().__init__()
        assert len(ranks) == len(in_modes) + 1, \
            f"ranks must be length {len(in_modes) + 1}, got {len(ranks)}"
        assert ranks[0] == 1 and ranks[-1] == 1, \
            f"r0 and rd must be 1, got r0={ranks[0]}, rd={ranks[-1]}"
        
        self.in_modes = list(in_modes)
        self.out_modes = list(out_modes)
        self.ranks = list(ranks)
        self.num_embeddings = _prod(in_modes)
        self.embedding_dim = _prod(out_modes)
        self.use_dense_path = use_dense_path
        
        cores = []
        for k in range(len(in_modes)):
            G = torch.empty(self.ranks[k], self.out_modes[k], self.in_modes[k], self.ranks[k+1])
            nn.init.xavier_uniform_(G.view(self.ranks[k], -1))
            cores.append(nn.Parameter(G))
        self.cores = nn.ParameterList(cores)

    def reconstruct_weight(self) -> torch.Tensor:
        """Same contraction as TTLinear"""
        T = _contract_cores(list(self.cores))
        W = T.reshape(self.embedding_dim, self.num_embeddings).t()  # (vocab, dim)
        return W

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass: embedding lookup
        input_ids: (B, T)
        """
        # Cache reconstruction for efficiency
        if not hasattr(self, '_cached_weight') or self._cached_weight is None:
            W = self.reconstruct_weight()  # (vocab, dim)
            if not self.training:  # Cache in eval mode
                self._cached_weight = W
        else:
            W = self._cached_weight
        
        return torch.nn.functional.embedding(input_ids, W)
    
    def train(self, mode: bool = True):
        """Override train to clear cache"""
        super().train(mode)
        if mode:  # Clear cache when entering training mode
            if hasattr(self, '_cached_weight'):
                self._cached_weight = None
        return self

    def copy_from_dense(self, weight: torch.Tensor):
        """Init cores by TT-SVD of an embedding table of shape (num_embeddings, embedding_dim)."""
        # Cores hold W^T (see reconstruct_weight)
        cores = tt_svd_init_from_dense(weight.detach().t(), self.in_modes, self.out_modes, self.ranks)
        with torch.no_grad():
            for core, c in zip(self.cores, cores):
                core.copy_(c)
        self._cached_weight = None
