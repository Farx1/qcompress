#!/usr/bin/env python3
"""
Script de test d'installation pour quantum-inspired-compression.
Vérifie que tous les composants principaux fonctionnent correctement.
"""

import sys
import torch
import yaml
import os

def test_imports():
    """Test des imports principaux."""
    print("🔍 Test des imports...")
    
    try:
        from src.tn.tt_layers import TTLinear, TTEmbedding, tt_svd_init_from_dense
        from src.tn.penalties import attach_penalty_to_module, PenaltyCollector
        from src.tn.math_utils import renyi_entropy, shannon_entropy
        from src.qtc.recipe import Recipe, Target, load_recipe
        from src.qtc.apply import apply_recipe_to_model, count_params
        from src.qtc.validator import validate_recipe, RecipeValidator
        print("✅ Tous les imports réussis")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_tt_layers():
    """Test des couches TT."""
    print("\n🔍 Test des couches TT...")
    
    try:
        from src.tn.tt_layers import TTLinear, TTEmbedding
        
        # Test TTLinear
        layer = TTLinear([4, 4], [4, 4], [1, 2, 1])
        x = torch.randn(2, 16)
        y = layer(x)
        assert y.shape == (2, 16)
        print("✅ TTLinear fonctionne")
        
        # Test TTEmbedding
        emb_layer = TTEmbedding([4, 4], [4, 4], [1, 2, 1])
        input_ids = torch.randint(0, 16, (2, 3))
        embeddings = emb_layer(input_ids)
        assert embeddings.shape == (2, 3, 16)
        print("✅ TTEmbedding fonctionne")
        
        # Test reconstruction
        W = layer.reconstruct_weight()
        assert W.shape == (16, 16)
        print("✅ Reconstruction des poids fonctionne")
        
        return True
    except Exception as e:
        print(f"❌ Erreur dans les couches TT: {e}")
        return False

def test_tt_svd_init():
    """Test de l'initialisation TT-SVD."""
    print("\n🔍 Test de l'initialisation TT-SVD...")
    
    try:
        from src.tn.tt_layers import tt_svd_init_from_dense
        
        W = torch.randn(16, 16)
        cores = tt_svd_init_from_dense(W, [4, 4], [4, 4], [1, 4, 1])
        assert len(cores) == 2
        assert cores[0].shape == (1, 4, 4, 4)
        assert cores[1].shape == (4, 4, 4, 1)
        print("✅ Initialisation TT-SVD fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur dans TT-SVD: {e}")
        return False

def test_penalties():
    """Test des pénalités."""
    print("\n🔍 Test des pénalités...")
    
    try:
        from src.tn.math_utils import renyi_entropy, shannon_entropy
        
        # Test entropie Rényi
        sv = torch.tensor([0.5, 0.3, 0.2])
        renyi = renyi_entropy(sv, alpha=2.0)
        assert isinstance(renyi, torch.Tensor)
        
        # Test entropie Shannon
        shannon = shannon_entropy(sv)
        assert isinstance(shannon, torch.Tensor)
        
        print("✅ Pénalités fonctionnent")
        return True
    except Exception as e:
        print(f"❌ Erreur dans les pénalités: {e}")
        return False

def test_recipe():
    """Test des recettes."""
    print("\n🔍 Test des recettes...")
    
    try:
        from src.qtc.recipe import Recipe, Target
        
        # Test création de recette
        target = Target(
            path="test.path",
            decomp="TT",
            in_modes=[4, 4],
            out_modes=[4, 4],
            ranks=[1, 2, 1]
        )
        
        recipe = Recipe(
            model="test_model",
            seed=42,
            budget="10x",
            targets=[target]
        )
        
        assert recipe.model == "test_model"
        assert len(recipe.targets) == 1
        
        print("✅ Recettes fonctionnent")
        return True
    except Exception as e:
        print(f"❌ Erreur dans les recettes: {e}")
        return False

def test_validation():
    """Test de la validation."""
    print("\n🔍 Test de la validation...")
    
    try:
        from src.qtc.validator import validate_recipe, RecipeValidator
        
        validator = RecipeValidator()
        assert len(validator.errors) == 0
        
        # Test validation de recette
        recipe_data = {
            'model': 'test',
            'targets': [
                {
                    'path': 'test.path',
                    'decomp': 'TT',
                    'in_modes': [4, 4],
                    'out_modes': [4, 4],
                    'ranks': [1, 2, 1],
                    'init': 'random'
                }
            ]
        }
        
        # Créer un modèle mock pour la validation
        class MockModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.test = torch.nn.Linear(16, 16)
        
        model = MockModel()
        is_valid, errors, warnings = validate_recipe(recipe_data, model)
        
        print("✅ Validation fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur dans la validation: {e}")
        return False

def test_example_recipe():
    """Test de la recette d'exemple."""
    print("\n🔍 Test de la recette d'exemple...")
    
    try:
        from src.qtc.recipe import load_recipe
        
        recipe_path = "examples/gpt2_tt.yaml"
        if os.path.exists(recipe_path):
            recipe = load_recipe(recipe_path)
            assert recipe.model == "gpt2"
            assert len(recipe.targets) > 0
            print("✅ Recette d'exemple chargée")
            return True
        else:
            print("⚠️  Recette d'exemple non trouvée (normal si pas encore créée)")
            return True
    except Exception as e:
        print(f"❌ Erreur dans la recette d'exemple: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🚀 Test d'installation - Quantum-Inspired Compression")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_tt_layers,
        test_tt_svd_init,
        test_penalties,
        test_recipe,
        test_validation,
        test_example_recipe
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Installation réussie ! Tous les composants fonctionnent.")
        print("\nProchaines étapes:")
        print("1. python scripts/train_qtc.py --recipe examples/gpt2_tt.yaml --steps 100")
        print("2. pytest tests/ -v")
        return 0
    else:
        print("❌ Certains tests ont échoué. Vérifiez l'installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 