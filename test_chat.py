#!/usr/bin/env python3
"""
Test rapide de la fonctionnalité de chat QCompress.
"""

import os
import sys
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Imports directs
import tn.tt_layers


def test_chat_generation():
    """Test de génération de chat"""
    print("Testing chat generation...")
    
    try:
        # Charger un petit modèle
        model_name = "distilgpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Forcer CPU
        device = torch.device('cpu')
        model = model.to(device)
        
        print(f"✅ Modèle {model_name} chargé")
        
        # Test de génération
        prompt = "Hello, how are you?"
        print(f"\nPrompt: {prompt}")
        
        # Tokeniser
        inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
        
        # Générer
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        generation_time = time.time() - start_time
        
        # Décoder
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        prompt_length = len(tokenizer.decode(inputs[0], skip_special_tokens=True))
        generated_text = response[prompt_length:].strip()
        
        print(f"✅ Génération réussie")
        print(f"  Réponse: {generated_text}")
        print(f"  Temps: {generation_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans la génération: {e}")
        return False


def test_compressed_chat():
    """Test de chat avec modèle compressé"""
    print("\nTesting compressed chat...")
    
    try:
        # Charger le modèle
        model_name = "distilgpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Forcer CPU
        device = torch.device('cpu')
        model = model.to(device)
        
        # Créer le modèle compressé
        compression_configs = {
            'lm_head': {
                'in_modes': [16, 16, 3],
                'out_modes': [17, 17, 17],
                'ranks': [1, 16, 16, 1]
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
        
        # Test de génération avec modèle compressé
        prompt = "What is Tensor-Train compression?"
        print(f"\nPrompt: {prompt}")
        
        # Tokeniser
        inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
        
        # Générer
        start_time = time.time()
        with torch.no_grad():
            outputs = compressed_model.generate(
                inputs,
                max_length=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        generation_time = time.time() - start_time
        
        # Décoder
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        prompt_length = len(tokenizer.decode(inputs[0], skip_special_tokens=True))
        generated_text = response[prompt_length:].strip()
        
        print(f"✅ Génération compressée réussie")
        print(f"  Réponse: {generated_text}")
        print(f"  Temps: {generation_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans la génération compressée: {e}")
        return False


def test_chat_parameters():
    """Test des paramètres de chat"""
    print("\nTesting chat parameters...")
    
    try:
        # Charger le modèle
        model_name = "distilgpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        device = torch.device('cpu')
        model = model.to(device)
        
        prompt = "Write a short story"
        
        # Test avec différentes températures
        temperatures = [0.1, 0.7, 1.5]
        
        for temp in temperatures:
            print(f"\n  Température: {temp}")
            
            inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
            
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=80,
                    temperature=temp,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            generation_time = time.time() - start_time
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            prompt_length = len(tokenizer.decode(inputs[0], skip_special_tokens=True))
            generated_text = response[prompt_length:].strip()
            
            print(f"    Temps: {generation_time:.2f}s")
            print(f"    Réponse: {generated_text[:50]}...")
        
        print("✅ Tests de paramètres réussis")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans les tests de paramètres: {e}")
        return False


def main():
    """Test principal"""
    print("🧪 Test de la fonctionnalité de chat QCompress")
    print("=" * 50)
    
    tests = [
        test_chat_generation,
        test_compressed_chat,
        test_chat_parameters
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
        print("🎉 Tous les tests sont passés ! La fonctionnalité de chat est prête.")
        print("\nPour tester le chat:")
        print("1. Lancez l'interface: python run_interface.py")
        print("2. Allez dans l'onglet '💬 Chat Test'")
        print("3. Configurez la compression dans la sidebar")
        print("4. Testez vos prompts !")
    else:
        print("❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main()) 