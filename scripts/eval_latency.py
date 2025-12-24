import argparse, time, torch
from transformers import AutoTokenizer, AutoModelForCausalLM


def parse_args():
    p = argparse.ArgumentParser(description='Évaluation de latence pour modèles compressés')
    p.add_argument('--ckpt', type=str, required=True, help='Chemin vers le checkpoint')
    p.add_argument('--prompt', type=str, default='Hello world', help='Prompt de test')
    p.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    p.add_argument('--max-new-tokens', type=int, default=128, help='Nombre de tokens à générer')
    p.add_argument('--num-runs', type=int, default=5, help='Nombre de runs pour la moyenne')
    p.add_argument('--warmup-runs', type=int, default=3, help='Nombre de runs de warmup')
    return p.parse_args()


def main():
    args = parse_args()
    
    print(f"Chargement du modèle depuis: {args.ckpt}")
    model = AutoModelForCausalLM.from_pretrained(args.ckpt).to(args.device)
    tok = AutoTokenizer.from_pretrained(args.ckpt)
    
    # Tokenisation du prompt
    inputs = tok(args.prompt, return_tensors='pt').to(args.device)
    
    print(f"Prompt: '{args.prompt}'")
    print(f"Tokens d'entrée: {inputs['input_ids'].shape}")
    print(f"Device: {args.device}")
    print(f"Modèle: {type(model).__name__}")
    
    # Warmup
    print(f"\nWarmup ({args.warmup_runs} runs)...")
    model.eval()
    with torch.no_grad():
        for i in range(args.warmup_runs):
            _ = model.generate(**inputs, max_new_tokens=32)
            if i % 2 == 0:
                print(f"  Warmup {i+1}/{args.warmup_runs}")
    
    # Synchronisation GPU si nécessaire
    if args.device == 'cuda':
        torch.cuda.synchronize()
    
    # Mesures de latence
    print(f"\nMesures de latence ({args.num_runs} runs)...")
    generation_times = []
    
    with torch.no_grad():
        for i in range(args.num_runs):
            # Synchronisation avant mesure
            if args.device == 'cuda':
                torch.cuda.synchronize()
            
            start_time = time.time()
            
            # Génération
            outputs = model.generate(
                **inputs, 
                max_new_tokens=args.max_new_tokens,
                do_sample=False,  # Déterministe pour la mesure
                pad_token_id=tok.eos_token_id
            )
            
            # Synchronisation après génération
            if args.device == 'cuda':
                torch.cuda.synchronize()
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            generation_times.append(generation_time)
            
            # Affichage du premier run
            if i == 0:
                generated_text = tok.decode(outputs[0], skip_special_tokens=True)
                print(f"  Texte généré: {generated_text}")
            
            print(f"  Run {i+1}: {generation_time:.3f}s")
    
    # Statistiques
    avg_time = sum(generation_times) / len(generation_times)
    min_time = min(generation_times)
    max_time = max(generation_times)
    
    # Calcul des tokens par seconde
    tokens_per_sec = args.max_new_tokens / avg_time
    
    # Résultats
    print(f"\n" + "="*50)
    print("RÉSULTATS DE LATENCE")
    print("="*50)
    print(f"Temps moyen: {avg_time:.3f}s ± {max_time - min_time:.3f}s")
    print(f"Temps min: {min_time:.3f}s")
    print(f"Temps max: {max_time:.3f}s")
    print(f"Tokens générés: {args.max_new_tokens}")
    print(f"Tokens/sec: {tokens_per_sec:.1f}")
    print(f"Latence par token: {avg_time/args.max_new_tokens*1000:.1f}ms")
    
    # Sauvegarde des résultats
    results = {
        'checkpoint': args.ckpt,
        'prompt': args.prompt,
        'device': args.device,
        'max_new_tokens': args.max_new_tokens,
        'num_runs': args.num_runs,
        'warmup_runs': args.warmup_runs,
        'generation_times': generation_times,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'tokens_per_sec': tokens_per_sec,
        'latency_per_token_ms': avg_time/args.max_new_tokens*1000
    }
    
    import json
    results_file = f"latency_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nRésultats sauvegardés dans: {results_file}")


if __name__ == '__main__':
    main() 