"""Property tests for TT-SVD and the TT layers, each checked against a dense oracle.

The math is in docs/THEORY.md. Everything runs in float64 so tolerances are tight.
"""
import itertools
import math

import pytest
import torch
from torch.func import functional_call

from src.tn.tt_layers import TTEmbedding, TTLinear, _contract_cores, tt_svd_init_from_dense

# (out_modes, in_modes): d = 2, 3 and 4, square and rectangular, some modes of size 1
SHAPES = [
    ([4, 4], [4, 4]),
    ([2, 3], [5, 2]),
    ([2, 3, 4], [3, 2, 2]),
    ([3, 1, 2], [2, 2, 3]),
    ([2, 2, 2, 2], [2, 3, 1, 2]),
]


def unfolding(W, out_modes, in_modes, k):
    """k-th TT unfolding: rows (m_1 n_1)...(m_k n_k), columns the rest."""
    d = len(in_modes)
    T = W.reshape(*out_modes, *in_modes).permute(*[i for j in range(d) for i in (j, d + j)])
    return T.reshape(math.prod(m * n for m, n in zip(out_modes[:k], in_modes[:k])), -1)


def full_ranks(out_modes, in_modes):
    a = [m * n for m, n in zip(out_modes, in_modes)]
    return [min(math.prod(a[:k]), math.prod(a[k:])) for k in range(len(a) + 1)]


def dense_from_cores(cores, out_modes, in_modes):
    """Oracle: W[t, l] = G_1[i_1, j_1] ... G_d[i_d, j_d] (Novikov et al. 2015, Eq. 3), entry by entry."""
    W = torch.zeros(math.prod(out_modes), math.prod(in_modes), dtype=torch.float64)
    for i in itertools.product(*map(range, out_modes)):
        for j in itertools.product(*map(range, in_modes)):
            p = torch.ones(1, 1, dtype=torch.float64)
            for G, ik, jk in zip(cores, i, j):
                p = p @ G[:, ik, jk, :]
            W[_ravel(i, out_modes), _ravel(j, in_modes)] = p.item()
    return W


def _ravel(idx, modes):
    r = 0
    for i, m in zip(idx, modes):
        r = r * m + i
    return r


def contract(cores, out_modes, in_modes):
    return _contract_cores(cores).reshape(math.prod(out_modes), math.prod(in_modes))


@pytest.mark.parametrize("out_modes,in_modes", SHAPES)
def test_full_rank_is_exact(out_modes, in_modes):
    torch.manual_seed(0)
    W = torch.randn(math.prod(out_modes), math.prod(in_modes), dtype=torch.float64)
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, full_ranks(out_modes, in_modes))
    torch.testing.assert_close(contract(cores, out_modes, in_modes), W, atol=1e-10, rtol=0)


@pytest.mark.parametrize("out_modes,in_modes", SHAPES)
@pytest.mark.parametrize("seed", range(3))
def test_truncated_error_within_ttsvd_bound(out_modes, in_modes, seed):
    """max_k eps_k <= ||W - W_tt||_F <= sqrt(sum_k eps_k^2), eps_k from an independent SVD."""
    g = torch.Generator().manual_seed(seed)
    W = torch.randn(math.prod(out_modes), math.prod(in_modes), dtype=torch.float64, generator=g)
    full = full_ranks(out_modes, in_modes)
    ranks = [1] + [max(1, int(r * torch.rand(1, generator=g))) for r in full[1:-1]] + [1]
    err = torch.linalg.norm(W - contract(tt_svd_init_from_dense(W, in_modes, out_modes, ranks), out_modes, in_modes))
    eps = [torch.linalg.svdvals(unfolding(W, out_modes, in_modes, k))[ranks[k]:].norm()
           for k in range(1, len(in_modes))]
    assert max(eps) - 1e-10 <= err <= torch.stack(eps).norm() + 1e-10, (ranks, err, eps)


@pytest.mark.parametrize("out_modes,in_modes", SHAPES)
def test_parameter_count_matches_closed_form(out_modes, in_modes):
    ranks = full_ranks(out_modes, in_modes)
    layer = TTLinear(in_modes, out_modes, ranks, bias=False)
    n_tt = sum(p.numel() for p in layer.parameters())
    assert n_tt == sum(ranks[k] * m * n * ranks[k + 1] for k, (m, n) in enumerate(zip(out_modes, in_modes)))
    # THEORY.md section 5: full TT rank never compresses
    assert n_tt > math.prod(out_modes) * math.prod(in_modes)


@pytest.mark.parametrize("out_modes,in_modes", SHAPES)
def test_ttlinear_forward_matches_dense_oracle(out_modes, in_modes):
    torch.manual_seed(0)
    layer = TTLinear(in_modes, out_modes, [1] + [2] * (len(in_modes) - 1) + [1]).double()
    with torch.no_grad():
        layer.bias.normal_()
    W = dense_from_cores(list(layer.cores), out_modes, in_modes)
    x = torch.randn(5, layer.in_features, dtype=torch.float64)
    expected = x @ W.T + layer.bias
    torch.testing.assert_close(layer.train()(x), expected, atol=1e-12, rtol=0)
    torch.testing.assert_close(layer.eval()(x), expected, atol=1e-12, rtol=0)  # cached path


def test_ttembedding_lookup_matches_dense_row():
    torch.manual_seed(0)
    vocab_modes, dim_modes = [3, 4], [2, 3]
    emb = TTEmbedding(vocab_modes, dim_modes, [1, 3, 1]).double()
    table = dense_from_cores(list(emb.cores), dim_modes, vocab_modes).T  # (vocab, dim)
    ids = torch.tensor([[0, 5, 11], [7, 7, 2]])
    torch.testing.assert_close(emb(ids), table[ids], atol=1e-12, rtol=0)


def test_ttembedding_copy_from_dense_full_rank_is_exact():
    torch.manual_seed(0)
    table = torch.randn(12, 6, dtype=torch.float64)
    emb = TTEmbedding([3, 4], [2, 3], [1, 6, 1]).double()
    emb.copy_from_dense(table)
    torch.testing.assert_close(emb.reconstruct_weight(), table, atol=1e-10, rtol=0)


def test_ttlinear_gradcheck():
    torch.manual_seed(0)
    layer = TTLinear([2, 3], [3, 2], [1, 2, 1]).double()
    x = torch.randn(2, 6, dtype=torch.float64, requires_grad=True)
    cores = [c.detach().clone().requires_grad_() for c in layer.cores]

    def f(x, *cores):
        return functional_call(layer, {f"cores.{k}": c for k, c in enumerate(cores)}, (x,))

    assert torch.autograd.gradcheck(f, (x, *cores))
