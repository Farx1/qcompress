import pytest
from torch import nn
from src.qtc.apply import apply_recipe_to_model, make_tt_module_from_dense
from src.qtc.recipe import Recipe, Target


def test_embedding_mode_mismatch_reports_error_instead_of_hanging():
    model = nn.Module()
    model.wte = nn.Embedding(10, 4)  # 10 has no [2, 2] factorization; used to loop forever
    recipe = Recipe(model='tiny', targets=[
        Target(path='wte', decomp='TT', in_modes=[2, 2], out_modes=[2, 2], ranks=[1, 2, 1]),
    ])
    summary = apply_recipe_to_model(model, recipe)
    assert summary['replaced'] == []
    assert 'mode products must match' in summary['errors'][0]
    assert isinstance(model.wte, nn.Embedding)


@pytest.mark.parametrize('in_modes', [[2, 2], [4, 4]])  # product too small / too large
def test_make_tt_module_rejects_mismatched_modes(in_modes):
    with pytest.raises(ValueError):
        make_tt_module_from_dense(nn.Embedding(10, 4), in_modes, [2, 2], [1, 2, 1])
    with pytest.raises(ValueError):
        make_tt_module_from_dense(nn.Linear(10, 4), in_modes, [2, 2], [1, 2, 1])
