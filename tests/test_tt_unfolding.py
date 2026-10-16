import math

import torch

from src.tn.math_utils import renyi_entropy, unfolding_singular_values
from src.tn.penalties import attach_penalty_to_module
from src.tn.tt_layers import TTEmbedding, TTLinear, _contract_cores, tt_svd_init_from_dense


def test_unfolding_svals_match_ttsvd_first_step():
    """k=1 unfolding is exactly the matrix TT-SVD decomposes first."""
    torch.manual_seed(0)
    layer = TTLinear([3, 2, 2], [2, 3, 4], [1, 2, 2, 1])
    W = torch.randn(24, 12, dtype=torch.float64)
    first = W.reshape(2, 3, 4, 3, 2, 2).permute(0, 3, 1, 4, 2, 5).reshape(2 * 3, -1)
    torch.testing.assert_close(unfolding_singular_values(W, layer)[0], torch.linalg.svdvals(first))


def test_unfolding_ranks_are_the_tt_ranks():
    """W built from cores with TT ranks (1, 2, 3, 1): unfolding k has exactly r_k nonzero singular values,
    and TT-SVD with those ranks is exact (Oseledets 2011)."""
    torch.manual_seed(0)
    out_modes, in_modes, ranks = [2, 3, 2], [3, 2, 2], [1, 2, 3, 1]
    cores = [torch.randn(ranks[k], out_modes[k], in_modes[k], ranks[k + 1], dtype=torch.float64) for k in range(3)]
    W = _contract_cores(cores).reshape(math.prod(out_modes), math.prod(in_modes))
    layer = TTLinear(in_modes, out_modes, ranks)
    svs = unfolding_singular_values(W, layer)
    for k, s in enumerate(svs, start=1):
        assert int((s > 1e-10 * s[0]).sum()) == ranks[k], (k, s)
    W_tt = _contract_cores(tt_svd_init_from_dense(W, in_modes, out_modes, ranks)).reshape(W.shape)
    torch.testing.assert_close(W_tt, W, atol=1e-10, rtol=0)


def test_embedding_penalty_uses_tt_matrix():
    torch.manual_seed(0)
    emb = TTEmbedding([4, 4], [2, 3], [1, 2, 1])
    attach_penalty_to_module(emb, {"type": "renyi", "alpha": 2.0, "lambda": 1.0})
    emb.train()(torch.tensor([[0, 5]]))
    W_tt = _contract_cores(list(emb.cores)).reshape(emb.embedding_dim, emb.num_embeddings).detach()
    expected = sum(renyi_entropy(s, alpha=2.0) for s in unfolding_singular_values(W_tt, emb))
    torch.testing.assert_close(emb._extra_loss, expected)
    # rank 2 => second singular value pair only; a wrong unfolding would show more
    assert int((unfolding_singular_values(W_tt, emb)[0] > 1e-6).sum()) == 2
