import torch
from transformers import GPT2Config, GPT2LMHeadModel
from transformers.pytorch_utils import Conv1D
from src.qtc.apply import apply_recipe_to_model
from src.qtc.recipe import Recipe, Target
from src.tn.tt_layers import TTLinear, TTEmbedding


def test_gpt2_tiny_full_rank_ttsvd_matches_original():
    """Random tiny GPT-2 (no download): full-rank TT-SVD must reproduce the logits."""
    torch.manual_seed(0)
    config = GPT2Config(vocab_size=64, n_positions=16, n_embd=16, n_layer=1, n_head=2)
    model = GPT2LMHeadModel(config).eval()
    assert isinstance(model.transformer.h[0].mlp.c_fc, Conv1D)
    ids = torch.randint(0, 64, (2, 8))
    with torch.no_grad():
        ref = model(ids).logits

    # Ranks = max rank of the (m1*n1, m2*n2) unfolding, i.e. exact TT
    recipe = Recipe(model='tiny-gpt2', targets=[
        Target('transformer.wte', 'TT', [8, 8], [4, 4], [1, 32, 1], init='ttsvd'),
        Target('transformer.h[*].attn.c_attn', 'TT', [4, 4], [8, 6], [1, 24, 1], init='ttsvd'),
        Target('transformer.h[*].mlp.c_fc', 'TT', [4, 4], [8, 8], [1, 32, 1], init='copy'),
        Target('transformer.h[*].mlp.c_proj', 'TT', [8, 8], [4, 4], [1, 32, 1], init='ttsvd'),
    ])
    summary = apply_recipe_to_model(model, recipe)
    assert summary['errors'] == []
    assert isinstance(model.transformer.wte, TTEmbedding)
    assert isinstance(model.transformer.h[0].mlp.c_fc, TTLinear)

    with torch.no_grad():
        out = model.eval()(ids).logits
    assert torch.allclose(out, ref, atol=1e-4), (out - ref).abs().max()
