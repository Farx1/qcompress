#!/usr/bin/env python3
"""
Test rapide de l'interface QCompress.
"""

import os
import sys
import tempfile
import json

def test_interface_imports():
    """Test des imports de l'interface"""
    print("Testing interface imports...")
    
    try:
        # Test des imports principaux
        import torch
        import numpy as np
        
        print("✅ Imports de base réussis")
        
        # Test des imports du projet
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        import tn.tt_layers
        import tn.math_utils
        
        print("✅ Imports du projet réussis")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False


def test_tt_layer_creation():
    """Test de création de couches TT"""
    print("\nTesting TT layer creation...")
    
    try:
        import torch
        from torch import nn
        import tn.tt_layers
        
        # Test TTLinear
        tt_linear = tn.tt_layers.TTLinear(
            in_modes=[16, 16, 3],
            out_modes=[64, 12, 4],
            ranks=[1, 16, 16, 1],
            bias=True,
            use_dense_path=True
        )
        
        # Test TTEmbedding
        tt_embedding = tn.tt_layers.TTEmbedding(
            in_modes=[17, 17, 17],
            out_modes=[16, 16, 3],
            ranks=[1, 16, 16, 1],
            use_dense_path=True
        )
        
        print("✅ Couches TT créées avec succès")
        print(f"  TTLinear paramètres: {sum(p.numel() for p in tt_linear.parameters()):,}")
        print(f"  TTEmbedding paramètres: {sum(p.numel() for p in tt_embedding.parameters()):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans la création des couches TT: {e}")
        return False


def test_model_loading():
    """Test de chargement de modèle"""
    print("\nTesting model loading...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Test avec un petit modèle
        model_name = "distilgpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        print(f"✅ Modèle {model_name} chargé avec succès")
        print(f"  Paramètres: {sum(p.numel() for p in model.parameters()):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle: {e}")
        return False


def test_compression_creation():
    """Test de création de modèle compressé"""
    print("\nTesting compression creation...")
    
    try:
        from transformers import AutoModelForCausalLM
        import torch
        import tn.tt_layers
        
        # Charger un modèle
        model = AutoModelForCausalLM.from_pretrained("distilgpt2")
        
        # Créer une configuration de compression
        compression_configs = {
            'lm_head': {
                'in_modes': [16, 16, 3],
                'out_modes': [17, 17, 17],
                'ranks': [1, 16, 16, 1]
            }
        }
        
        # Créer le modèle compressé
        compressed_model = type(model).from_pretrained("distilgpt2")
        
        # Remplacer lm_head
        original_lm_head = model.lm_head
        tt_layer = tn.tt_layers.TTLinear(
            in_modes=compression_configs['lm_head']['in_modes'],
            out_modes=compression_configs['lm_head']['out_modes'],
            ranks=compression_configs['lm_head']['ranks'],
            bias=(original_lm_head.bias is not None),
            use_dense_path=True
        )
        compressed_model.lm_head = tt_layer
        
        # Comparer les paramètres
        original_params = sum(p.numel() for p in model.parameters())
        compressed_params = sum(p.numel() for p in compressed_model.parameters())
        compression_ratio = original_params / compressed_params
        
        print("✅ Modèle compressé créé avec succès")
        print(f"  Compression: {compression_ratio:.2f}x")
        print(f"  Original: {original_params:,} paramètres")
        print(f"  Compressé: {compressed_params:,} paramètres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du modèle compressé: {e}")
        return False


def test_visualization():
    """Test de création de visualisations (données uniquement)"""
    print("\nTesting visualization data creation...")
    
    try:
        # Créer des données de test
        original_stats = {
            'parameters': 1000000,
            'size_mb': 500.0,
            'speed': {'avg_time': 0.1}
        }
        
        compressed_stats = {
            'parameters': 200000,
            'size_mb': 100.0,
            'speed': {'avg_time': 0.2}
        }
        
        compression_ratio = original_stats['parameters'] / compressed_stats['parameters']
        
        print("✅ Données de visualisation créées avec succès")
        print(f"  Compression ratio: {compression_ratio:.2f}x")
        print(f"  Original: {original_stats['parameters']:,} paramètres")
        print(f"  Compressé: {compressed_stats['parameters']:,} paramètres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données: {e}")
        return False


def main():
    """Test principal"""
    print("🧪 Test de l'interface QCompress")
    print("=" * 50)
    
    tests = [
        test_interface_imports,
        test_tt_layer_creation,
        test_model_loading,
        test_compression_creation,
        test_visualization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'interface est prête.")
        print("\nPour lancer l'application:")
        print("  Windows: .\\start.ps1")
        print("  Linux/Mac: ./start.sh")
        print("\nOu manuellement:")
        print("  Backend: cd backend && python -m uvicorn main:app --reload")
        print("  Frontend: cd frontend && npm run dev")
    else:
        print("❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main()) 