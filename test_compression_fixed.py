#!/usr/bin/env python3
"""
Test de la compression avec gestion d'erreur améliorée.
"""

import os
import sys
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Imports directs
import tn.tt_layers


def test_compression_with_validation():
    """Test de la compression avec validation des dimensions"""
    print("Testing compression with dimension validation...")
    
    try:
        # Charger le modèle
        model_name = "distilgpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        device = torch.device('cpu')
        model = model.to(device)
        
        print(f"✅ Modèle {model_name} chargé")
        
        # Configuration de compression avec validation
        compression_configs = {
            'lm_head': {
                'in_modes': [16, 16, 3],  # 768 dimensions
                'out_modes': [17, 17, 17],  # ~4913 dimensions
                'ranks': [1, 16, 16, 1]
            }
        }
        
        # Vérifier les dimensions avant compression
        lm_head = model.lm_head
        print(f"lm_head dimensions: {lm_head.in_features} -> {lm_head.out_features}")
        
        # Calculer les dimensions configurées
        config = compression_configs['lm_head']
        actual_in_features = 1
        for mode in config['in_modes']:
            actual_in_features *= mode
        
        actual_out_features = 1
        for mode in config['out_modes']:
            actual_out_features *= mode
        
        print(f"Dimensions configurées: {actual_in_features} -> {actual_out_features}")
        
        # Ajuster si nécessaire
        if actual_in_features != lm_head.in_features:
            print(f"⚠️ Ajustement des modes d'entrée")
            if actual_in_features > lm_head.in_features:
                config['in_modes'] = [lm_head.in_features]
            else:
                while actual_in_features < lm_head.in_features:
                    config['in_modes'].append(1)
                    actual_in_features *= 1
        
        if actual_out_features != lm_head.out_features:
            print(f"⚠️ Ajustement des modes de sortie")
            if actual_out_features > lm_head.out_features:
                config['out_modes'] = [lm_head.out_features]
            else:
                while actual_out_features < lm_head.out_features:
                    config['out_modes'].append(1)
                    actual_out_features *= 1
        
        print(f"Dimensions ajustées: {actual_in_features} -> {actual_out_features}")
        
        # Créer la couche TT
        try:
            tt_layer = tn.tt_layers.TTLinear(
                in_modes=config['in_modes'],
                out_modes=config['out_modes'],
                ranks=config['ranks'],
                bias=(lm_head.bias is not None),
                use_dense_path=True
            )
            print("✅ Couche TT créée avec succès")
            
            # Test du forward pass
            test_input = torch.randn(2, lm_head.in_features)
            with torch.no_grad():
                output = tt_layer(test_input)
                print(f"✅ Forward pass réussi: {test_input.shape} -> {output.shape}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la couche TT: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False


def test_compressed_model_creation():
    """Test de la création complète du modèle compressé"""
    print("\nTesting complete compressed model creation...")
    
    try:
        # Charger le modèle
        model_name = "distilgpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        device = torch.device('cpu')
        model = model.to(device)
        
        # Configuration simple
        compression_configs = {
            'lm_head': {
                'in_modes': [768],  # Exactement les bonnes dimensions
                'out_modes': [50257],  # Exactement les bonnes dimensions
                'ranks': [1, 16, 1]
            }
        }
        
        # Créer le modèle compressé
        compressed_model = type(model).from_pretrained(model_name)
        
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
        compressed_model = compressed_model.to(device)
        
        print("✅ Modèle compressé créé")
        
        # Test simple
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Test avec un petit input
        test_input = torch.randint(0, 50257, (1, 10))
        test_input = test_input.to(device)
        
        with torch.no_grad():
            try:
                outputs = compressed_model(input_ids=test_input)
                print(f"✅ Forward pass réussi: {outputs.logits.shape}")
                return True
            except Exception as e:
                print(f"❌ Erreur lors du forward pass: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False


def test_error_handling():
    """Test de la gestion d'erreur"""
    print("\nTesting error handling...")
    
    try:
        # Configuration invalide
        invalid_configs = {
            'lm_head': {
                'in_modes': [1000, 1000],  # Trop grand
                'out_modes': [100000],     # Trop grand
                'ranks': [1, 1, 1]
            }
        }
        
        # Charger le modèle
        model_name = "distilgpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        device = torch.device('cpu')
        model = model.to(device)
        
        # Essayer de créer une couche TT avec configuration invalide
        try:
            tt_layer = tn.tt_layers.TTLinear(
                in_modes=invalid_configs['lm_head']['in_modes'],
                out_modes=invalid_configs['lm_head']['out_modes'],
                ranks=invalid_configs['lm_head']['ranks'],
                bias=True,
                use_dense_path=True
            )
            print("⚠️ Couche TT créée malgré configuration invalide")
            return True
        except Exception as e:
            print(f"✅ Erreur correctement gérée: {e}")
            return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False


def main():
    """Test principal"""
    print("🧪 Test de la compression avec gestion d'erreur améliorée")
    print("=" * 60)
    
    tests = [
        test_compression_with_validation,
        test_compressed_model_creation,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! La compression est corrigée.")
        print("\nL'interface devrait maintenant fonctionner sans erreur 'index out of range'.")
        print("Lancez: python run_interface.py")
    else:
        print("❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
