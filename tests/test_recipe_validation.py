import pytest
import torch
from torch import nn
from src.qtc.recipe import Recipe, Target
from src.qtc.validator import validate_recipe, RecipeValidator, auto_adjust_embedding_modes


class MockModel(nn.Module):
    """Modèle mock pour les tests."""
    def __init__(self):
        super().__init__()
        self.transformer = nn.ModuleDict({
            'wte': nn.Embedding(50257, 768),
            'h': nn.ModuleList([
                nn.ModuleDict({
                    'mlp': nn.ModuleDict({
                        'c_fc': nn.Linear(768, 3072),
                        'c_proj': nn.Linear(3072, 768)
                    })
                }) for _ in range(12)
            ])
        })


def test_recipe_validator_basic():
    """Test de base du validateur de recettes."""
    validator = RecipeValidator()
    assert len(validator.errors) == 0
    assert len(validator.warnings) == 0


def test_validate_path():
    """Test de validation des chemins."""
    model = MockModel()
    validator = RecipeValidator()
    
    # Test de chemin valide
    target = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[17, 17, 17, 10],
        out_modes=[16, 16, 3],
        ranks=[1, 16, 16, 1]
    )
    
    assert validator._validate_path(target.path, model)
    
    # Test de chemin invalide
    target_invalid = Target(
        path="transformer.nonexistent",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, 2, 1]
    )
    
    assert not validator._validate_path(target_invalid.path, model)
    assert len(validator.errors) > 0


def test_validate_decomposition():
    """Test de validation des types de décomposition."""
    validator = RecipeValidator()
    
    # Test TT valide
    target_tt = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, 2, 1]
    )
    
    assert validator._validate_decomposition(target_tt.decomp)
    
    # Test décomposition non supportée
    target_invalid = Target(
        path="transformer.wte",
        decomp="MPO",  # Non supporté en v1
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, 2, 1]
    )
    
    assert not validator._validate_decomposition(target_invalid.decomp)
    assert len(validator.errors) > 0


def test_validate_dimensions():
    """Test de validation des dimensions."""
    model = MockModel()
    validator = RecipeValidator()
    
    # Test Linear valide
    target_linear = Target(
        path="transformer.h.0.mlp.c_fc",
        decomp="TT",
        in_modes=[16, 16, 3],  # 768
        out_modes=[64, 12, 4],  # 3072
        ranks=[1, 16, 16, 1]
    )
    
    assert validator._validate_dimensions(target_linear, model)
    
    # Test Linear avec dimensions incorrectes
    target_linear_invalid = Target(
        path="transformer.h.0.mlp.c_fc",
        decomp="TT",
        in_modes=[16, 16],  # 256 ≠ 768
        out_modes=[64, 12, 4],  # 3072
        ranks=[1, 16, 16, 1]
    )
    
    assert not validator._validate_dimensions(target_linear_invalid, model)
    assert len(validator.errors) > 0
    
    # Test Embedding valide
    target_embedding = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[17, 17, 17, 10],  # ≈ 50257
        out_modes=[16, 16, 3],  # 768
        ranks=[1, 16, 16, 1]
    )
    
    assert validator._validate_dimensions(target_embedding, model)
    
    # Test Embedding avec dimensions incorrectes
    target_embedding_invalid = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[17, 17, 17, 10],  # ≈ 50257
        out_modes=[16, 16],  # 256 ≠ 768
        ranks=[1, 16, 16, 1]
    )
    
    assert not validator._validate_dimensions(target_embedding_invalid, model)
    assert len(validator.errors) > 0


def test_validate_ranks():
    """Test de validation des rangs."""
    validator = RecipeValidator()
    
    # Test rangs valides
    target_valid = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, 2, 1]
    )
    
    assert validator._validate_ranks(target_valid)
    
    # Test rangs trop courts
    target_short = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, 2]  # Trop court
    )
    
    assert not validator._validate_ranks(target_short)
    assert len(validator.errors) > 0
    
    # Test r0 ≠ 1
    target_r0_invalid = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[2, 2, 1]  # r0 ≠ 1
    )
    
    assert not validator._validate_ranks(target_r0_invalid)
    assert len(validator.errors) > 0
    
    # Test rd ≠ 1
    target_rd_invalid = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, 2, 2]  # rd ≠ 1
    )
    
    assert not validator._validate_ranks(target_rd_invalid)
    assert len(validator.errors) > 0
    
    # Test rangs négatifs
    target_negative = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, -1, 1]  # Rang négatif
    )
    
    assert not validator._validate_ranks(target_negative)
    assert len(validator.errors) > 0


def test_validate_target():
    """Test de validation complète d'une cible."""
    model = MockModel()
    validator = RecipeValidator()
    
    # Test cible valide
    target_valid = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[17, 17, 17, 10],
        out_modes=[16, 16, 3],
        ranks=[1, 16, 16, 1]
    )
    
    assert validator.validate_target(target_valid, model)
    
    # Test cible invalide (chemin inexistant)
    target_invalid = Target(
        path="transformer.nonexistent",
        decomp="TT",
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[1, 2, 1]
    )
    
    assert not validator.validate_target(target_invalid, model)
    assert len(validator.errors) > 0


def test_validate_recipe():
    """Test de validation d'une recette complète."""
    model = MockModel()
    
    # Recette valide
    recipe_data_valid = {
        'model': 'gpt2',
        'targets': [
            {
                'path': 'transformer.wte',
                'decomp': 'TT',
                'in_modes': [17, 17, 17, 10],
                'out_modes': [16, 16, 3],
                'ranks': [1, 16, 16, 1],
                'init': 'random'
            },
            {
                'path': 'transformer.h.0.mlp.c_fc',
                'decomp': 'TT',
                'in_modes': [16, 16, 3],
                'out_modes': [64, 12, 4],
                'ranks': [1, 16, 16, 1],
                'init': 'random'
            }
        ]
    }
    
    is_valid, errors, warnings = validate_recipe(recipe_data_valid, model)
    assert is_valid
    assert len(errors) == 0
    
    # Recette invalide (champ manquant)
    recipe_data_invalid = {
        'model': 'gpt2'
        # 'targets' manquant
    }
    
    is_valid, errors, warnings = validate_recipe(recipe_data_invalid, model)
    assert not is_valid
    assert len(errors) > 0
    
    # Recette avec cible invalide
    recipe_data_bad_target = {
        'model': 'gpt2',
        'targets': [
            {
                'path': 'transformer.nonexistent',
                'decomp': 'TT',
                'in_modes': [4, 4],
                'out_modes': [4, 4],
                'ranks': [1, 2, 1],
                'init': 'random'
            }
        ]
    }
    
    is_valid, errors, warnings = validate_recipe(recipe_data_bad_target, model)
    assert not is_valid
    assert len(errors) > 0


def test_auto_adjust_embedding_modes():
    """Test de l'ajustement automatique des modes d'embedding."""
    model = MockModel()
    
    # Test avec modes corrects
    target_correct = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[17, 17, 17, 10],  # ≈ 50257
        out_modes=[16, 16, 3],
        ranks=[1, 16, 16, 1]
    )
    
    adjusted = auto_adjust_embedding_modes(target_correct, model)
    assert adjusted.in_modes == [17, 17, 17, 10]  # Pas de changement
    
    # Test avec modes incorrects (sera ajusté)
    target_incorrect = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[10, 10, 10, 10],  # 10000 ≠ 50257
        out_modes=[16, 16, 3],
        ranks=[1, 16, 16, 1]
    )
    
    adjusted = auto_adjust_embedding_modes(target_incorrect, model)
    # Les modes devraient être ajustés pour correspondre à 50257
    assert adjusted.in_modes != [10, 10, 10, 10]


def test_validator_error_messages():
    """Test des messages d'erreur du validateur."""
    model = MockModel()
    validator = RecipeValidator()
    
    # Test avec plusieurs erreurs
    target_invalid = Target(
        path="transformer.nonexistent",
        decomp="MPO",  # Non supporté
        in_modes=[4, 4],
        out_modes=[4, 4],
        ranks=[2, 2, 1]  # r0 ≠ 1
    )
    
    validator.validate_target(target_invalid, model)
    
    # Vérification des messages d'erreur
    error_messages = validator.get_errors()
    assert len(error_messages) > 0
    
    # Les messages devraient être informatifs
    for error in error_messages:
        assert len(error) > 10  # Messages non vides
        assert "Module" in error or "Décomposition" in error or "ranks" in error


def test_validator_warnings():
    """Test des avertissements du validateur."""
    model = MockModel()
    validator = RecipeValidator()
    
    # Test avec embedding qui nécessite un ajustement
    target_embedding = Target(
        path="transformer.wte",
        decomp="TT",
        in_modes=[17, 17, 17, 10],  # ≈ 50257
        out_modes=[16, 16, 3],
        ranks=[1, 16, 16, 1]
    )
    
    validator._validate_dimensions(target_embedding, model)
    
    # Vérification des avertissements
    warnings = validator.get_warnings()
    # Il peut y avoir des avertissements d'auto-ajustement
    assert isinstance(warnings, list)


def test_validator_clear():
    """Test de la fonction clear du validateur."""
    validator = RecipeValidator()
    
    # Ajouter des erreurs et avertissements
    validator.errors.append("Test error")
    validator.warnings.append("Test warning")
    
    assert len(validator.errors) > 0
    assert len(validator.warnings) > 0
    
    # Clear
    validator.clear()
    
    assert len(validator.errors) == 0
    assert len(validator.warnings) == 0


if __name__ == '__main__':
    pytest.main([__file__]) 