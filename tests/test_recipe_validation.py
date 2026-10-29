import pytest
from torch import nn
from src.qtc.recipe import Recipe, Target
from src.qtc.validator import validate_recipe, RecipeValidator


class MockModel(nn.Module):
    """Small GPT-2-shaped model: wte + 2 blocks of Linear MLPs."""
    def __init__(self):
        super().__init__()
        self.transformer = nn.ModuleDict({
            'wte': nn.Embedding(64, 16),
            'h': nn.ModuleList([
                nn.ModuleDict({'mlp': nn.ModuleDict({
                    'c_fc': nn.Linear(16, 64),
                    'c_proj': nn.Linear(64, 16),
                })}) for _ in range(2)
            ]),
        })


def target(path='transformer.h[*].mlp.c_fc', in_modes=(4, 4), out_modes=(8, 8), ranks=(1, 4, 1), **kw):
    return Target(path=path, decomp=kw.pop('decomp', 'TT'), in_modes=list(in_modes),
                  out_modes=list(out_modes), ranks=list(ranks), **kw)


def check(*targets):
    return validate_recipe(MockModel(), Recipe(model='mock', targets=list(targets)))


def test_valid_recipe():
    is_valid, errors, warnings = check(
        target(),
        target('transformer.h[*].mlp.c_proj', in_modes=(8, 8), out_modes=(4, 4)),
        target('transformer.wte', in_modes=(8, 8), out_modes=(4, 4)),
    )
    assert is_valid and errors == [] and warnings == []


@pytest.mark.parametrize('bad, needle', [
    (target('transformer.nonexistent'), 'Cannot access module'),
    (target('transformer.missing[*].mlp'), 'does not match any modules'),
    (target(in_modes=(4, 2)), 'in_modes product'),
    (target(out_modes=(8, 4)), 'out_modes product'),
    (target(ranks=(1, 4)), 'ranks length'),
    (target(ranks=(2, 4, 1)), 'start and end with 1'),
    (target(decomp='MPO'), "Only 'TT'"),
])
def test_invalid_targets(bad, needle):
    is_valid, errors, _ = check(bad)
    assert not is_valid
    assert any(needle in e for e in errors), errors


def test_unknown_init_is_warning():
    is_valid, errors, warnings = check(target(init='magic'))
    assert is_valid and errors == []
    assert any('Unknown init' in w for w in warnings)


def test_validator_resets_between_runs():
    v = RecipeValidator(MockModel())
    assert not v.validate(Recipe(model='mock', targets=[target(decomp='MPO')]))[0]
    assert v.validate(Recipe(model='mock', targets=[target()]))[0]
