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
        d = len(self.in_modes)
        idx_letters = list('abcdefghijklmnopqrstuvwxyz')
        assert d + 1 <= len(idx_letters) - 5, "Increase index alphabet for deeper TT"
        
        # Use rank indices: a, b, c, d, ...
        # Use mode indices: i, j, k, l, ... for output modes
        # Use mode indices: p, q, r, s, ... for input modes
        rank_letters = idx_letters[:d+1]  # a, b, c, d, ...
        out_mode_letters = idx_letters[d+1:d+1+d]  # i, j, k, ...
        in_mode_letters = idx_letters[d+1+d:d+1+2*d]  # p, q, r, ...
        
        terms = []
        for k in range(d):
            left_rank = rank_letters[k]
            right_rank = rank_letters[k+1]
            out_mode = out_mode_letters[k]
            in_mode = in_mode_letters[k]
            terms.append(f"{left_rank}{out_mode}{in_mode}{right_rank}")
        
        # Build equation
        eq_lhs = ', '.join(terms)
        # Output: all output modes followed by all input modes
        eq_rhs = ''.join(out_mode_letters[:d] + in_mode_letters[:d])
        eq = eq_lhs + '->' + eq_rhs
        
        # Contract
        operands = [core for core in self.cores]
        T = oe.contract(eq, *operands)  # shape (m1,...,md, n1,...,nd)
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

    def copy_from_dense(self, dense: nn.Linear):
        """Copy weights from a dense Linear layer (naive initialization)"""
        with torch.no_grad():
            # TODO: implement TT-SVD init for better initialization
            if dense.bias is not None and self.bias is not None:
                self.bias.copy_(dense.bias)


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
    from .math_utils import truncated_svd_singular_values
    
    # Reshape W to tensor form
    out_features = _prod(out_modes)
    in_features = _prod(in_modes)
    
    assert W.shape == (out_features, in_features), \
        f"W shape {W.shape} doesn't match ({out_features}, {in_features})"
    
    # Reshape to tensor: (m1, m2, ..., md, n1, n2, ..., nd)
    T = W.reshape(*out_modes, *in_modes)
    
    d = len(in_modes)
    cores = []
    remaining = T
    
    # Left-to-right sweep
    for k in range(d):
        # Reshape remaining tensor
        if k == 0:
            # First core: (m0, n0, m1, n1, ..., md-1, nd-1)
            left_dims = out_modes[0] * in_modes[0]
            right_dims = _prod(out_modes[1:]) * _prod(in_modes[1:])
            matrix = remaining.reshape(left_dims, right_dims)
        else:
            # Subsequent cores: (r_{k-1}, m_k, n_k, ...)
            r_prev = ranks[k]
            left_dims = r_prev * out_modes[k] * in_modes[k]
            right_dims = _prod(out_modes[k+1:]) * _prod(in_modes[k+1:]) if k < d - 1 else 1
            matrix = remaining.reshape(left_dims, right_dims)
        
        # SVD
        r_k = ranks[k+1] if k < d - 1 else 1
        U, S, Vh = torch.linalg.svd(matrix, full_matrices=False)
        
        # Truncate to rank r_k
        if len(S) > r_k:
            U = U[:, :r_k]
            S = S[:r_k]
            Vh = Vh[:r_k, :]
        
        # Form core: (r_{k-1}, m_k, n_k, r_k)
        if k == 0:
            core = (U * S.unsqueeze(0)).reshape(ranks[k], out_modes[k], in_modes[k], r_k)
        else:
            core = U.reshape(ranks[k], out_modes[k], in_modes[k], r_k)
        
        cores.append(core)
        
        # Update remaining tensor
        if k < d - 1:
            remaining = Vh.reshape(r_k, *out_modes[k+1:], *in_modes[k+1:])
    
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
        d = len(self.in_modes)
        idx_letters = list('abcdefghijklmnopqrstuvwxyz')
        
        # Use rank indices: a, b, c, d, ...
        # Use mode indices: i, j, k, l, ... for output modes
        # Use mode indices: p, q, r, s, ... for input modes
        rank_letters = idx_letters[:d+1]  # a, b, c, d, ...
        out_mode_letters = idx_letters[d+1:d+1+d]  # i, j, k, ...
        in_mode_letters = idx_letters[d+1+d:d+1+2*d]  # p, q, r, ...
        
        terms = []
        for k in range(d):
            left_rank = rank_letters[k]
            right_rank = rank_letters[k+1]
            out_mode = out_mode_letters[k]
            in_mode = in_mode_letters[k]
            terms.append(f"{left_rank}{out_mode}{in_mode}{right_rank}")
        
        # Build equation
        eq_lhs = ', '.join(terms)
        # Output: all output modes followed by all input modes
        eq_rhs = ''.join(out_mode_letters[:d] + in_mode_letters[:d])
        eq = eq_lhs + '->' + eq_rhs
        
        T = oe.contract(eq, *[c for c in self.cores])
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

    def copy_from_dense(self, emb: nn.Embedding):
        """Copy weights from a dense Embedding layer"""
        with torch.no_grad():
            # TODO: implement TT-SVD init
            pass

