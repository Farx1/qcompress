import torch
from typing import List, Optional

from .tt_layers import tt_tensor


def _prod(xs):
    """Helper to compute product of a list"""
    return int(torch.tensor(xs).prod().item()) if len(xs) > 0 else 1


def unfolding_singular_values(W: torch.Tensor, mod) -> List[torch.Tensor]:
    """
    Singular values of the TT unfoldings of a weight matrix.

    W is the (out_features, in_features) TT-matrix. It is reshaped to the
    interleaved tensor (m1, n1, ..., md, nd) that TT-SVD factorises, and the
    k-th unfolding groups the first k (m_i, n_i) pairs as rows (k = 1..d-1).
    Its rank is the smallest possible TT rank r_k.

    Args:
        W: Weight matrix of shape (out_features, in_features)
        mod: Module with in_modes and out_modes attributes

    Returns:
        List of singular value tensors for each unfolding
    """
    T = tt_tensor(W, mod.out_modes, mod.in_modes)
    pairs = [m * n for m, n in zip(mod.out_modes, mod.in_modes)]
    return [torch.linalg.svdvals(T.reshape(_prod(pairs[:k]), -1)) for k in range(1, len(pairs))]


def truncated_svd_singular_values(
    matrix: torch.Tensor, 
    rank: Optional[int] = None
) -> torch.Tensor:
    """
    Compute truncated SVD singular values of a matrix.
    
    Args:
        matrix: Input matrix
        rank: Maximum rank to keep (None for full SVD)
    
    Returns:
        Singular values tensor
    """
    U, S, Vh = torch.linalg.svd(matrix, full_matrices=False)
    if rank is not None and len(S) > rank:
        S = S[:rank]
    return S


def renyi_entropy(singular_values: torch.Tensor, alpha: float = 2.0) -> torch.Tensor:
    """
    Compute Rényi entropy of singular values.
    
    H_α(p) = (1/(1-α)) * log(Σ p_i^α)
    
    Args:
        singular_values: Singular values tensor
        alpha: Rényi parameter (α=1 gives Shannon entropy)
    
    Returns:
        Rényi entropy value
    """
    # Normalize to probabilities
    p = singular_values / (singular_values.sum() + 1e-12)
    
    if alpha == 1.0:
        # Shannon entropy (limit as α→1)
        return -(p * (p + 1e-12).log()).sum()
    else:
        return (1.0 / (1.0 - alpha)) * torch.log((p ** alpha).sum() + 1e-12)


def shannon_entropy(singular_values: torch.Tensor) -> torch.Tensor:
    """
    Compute Shannon entropy of singular values.
    
    H(p) = -Σ p_i * log(p_i)
    
    Args:
        singular_values: Singular values tensor
    
    Returns:
        Shannon entropy value
    """
    return renyi_entropy(singular_values, alpha=1.0)


def nuclear_norm(matrix: torch.Tensor) -> torch.Tensor:
    """
    Compute nuclear norm (sum of singular values) of a matrix.
    
    Args:
        matrix: Input matrix
    
    Returns:
        Nuclear norm value
    """
    _, S, _ = torch.linalg.svd(matrix, full_matrices=False)
    return S.sum()


def effective_rank(singular_values: torch.Tensor, threshold: float = 0.99) -> int:
    """
    Compute effective rank based on cumulative energy.
    
    Args:
        singular_values: Singular values tensor
        threshold: Cumulative energy threshold (default 0.99)
    
    Returns:
        Effective rank
    """
    sv_sorted = torch.sort(singular_values, descending=True)[0]
    cumulative = torch.cumsum(sv_sorted, dim=0)
    total = cumulative[-1]
    mask = cumulative <= (threshold * total)
    return mask.sum().item()

