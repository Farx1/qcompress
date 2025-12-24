#!/usr/bin/env python3
"""
Test simple pour vérifier que les composants de base fonctionnent.
"""

import torch
import sys

def test_basic_imports():
    """Test des imports de base."""
    print("🔍 Test des imports de base...")
    
    try:
        from src.tn.tt_layers import TTLinear, TTEmbedding
        from src.qtc.recipe import Recipe, Target
        print("✅ Imports de base réussis")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_simple_tt_linear():
    """Test simple d'une couche TT Linear."""
    print("\n🔍 Test simple TT Linear...")
    
    try:
        from src.tn.tt_layers import TTLinear
        
        # Test avec des dimensions simples
        layer = TTLinear([2, 2], [2, 2], [1, 1, 1])  # Rangs minimaux
        x = torch.randn(1, 4)
        y = layer(x)
        print(f"✅ TTLinear: input {x.shape} -> output {y.shape}")
        return True
    except Exception as e:
        print(f"❌ Erreur TTLinear: {e}")
        return False

def test_simple_tt_embedding():
    """Test simple d'une couche TT Embedding."""
    print("\n🔍 Test simple TT Embedding...")
    
    try:
        from src.tn.tt_layers import TTEmbedding
        
        # Test avec des dimensions simples
        layer = TTEmbedding([2, 2], [2, 2], [1, 1, 1])  # Rangs minimaux
        input_ids = torch.randint(0, 4, (1, 2))
        y = layer(input_ids)
        print(f"✅ TTEmbedding: input {input_ids.shape} -> output {y.shape}")
        return True
    except Exception as e:
        print(f"❌ Erreur TTEmbedding: {e}")
        return False

def test_recipe_basic():
    """Test de base des recettes."""
    print("\n🔍 Test des recettes...")
    
    try:
        from src.qtc.recipe import Recipe, Target
        
        target = Target(
            path="test.path",
            decomp="TT",
            in_modes=[2, 2],
            out_modes=[2, 2],
            ranks=[1, 1, 1]
        )
        
        recipe = Recipe(
            model="test_model",
            seed=42,
            budget="10x",
            targets=[target]
        )
        
        print(f"✅ Recette créée: {recipe.model} avec {len(recipe.targets)} cibles")
        return True
    except Exception as e:
        print(f"❌ Erreur recette: {e}")
        return False

def test_math_utils():
    """Test des utilitaires mathématiques."""
    print("\n🔍 Test des utilitaires mathématiques...")
    
    try:
        from src.tn.math_utils import renyi_entropy, shannon_entropy
        
        sv = torch.tensor([0.5, 0.3, 0.2])
        renyi = renyi_entropy(sv, alpha=2.0)
        shannon = shannon_entropy(sv)
        
        print(f"✅ Math utils: Rényi={renyi:.4f}, Shannon={shannon:.4f}")
        return True
    except Exception as e:
        print(f"❌ Erreur math utils: {e}")
        return False

def main():
    """Fonction principale."""
    print("🚀 Test simple - Quantum-Inspired Compression")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_simple_tt_linear,
        test_simple_tt_embedding,
        test_recipe_basic,
        test_math_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tests de base réussis !")
        return 0
    else:
        print("❌ Certains tests ont échoué.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 