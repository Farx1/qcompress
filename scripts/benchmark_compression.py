#!/usr/bin/env python3
"""
Benchmark script pour évaluer l'impact de la compression TT sur les performances.
Compare le modèle dense original avec le modèle compressé sur plusieurs métriques.
"""

import os
import sys
import argparse
import json
import time
import torch
import numpy as np
from torch import nn
from torch.utils.data import DataLoader
from datasets import load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    AutoModelForSequenceClassification,
    DataCollatorWithPadding
)
from accelerate import Accelerator
from tqdm import tqdm

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Imports directs pour éviter les problèmes d'imports relatifs
import qtc.recipe
import qtc.apply
import qtc.utils


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark compression impact on model performance")
    parser.add_argument('--model', type=str, default='gpt2', help='HuggingFace model name')
    parser.add_argument('--recipe', type=str, required=True, help='Path to compression recipe YAML')
    parser.add_argument('--dataset', type=str, default='wikitext-2-raw-v1', help='Dataset for evaluation')
    parser.add_argument('--task', type=str, default='language_modeling', 
                       choices=['language_modeling', 'classification'], help='Task type')
    parser.add_argument('--batch_size', type=int, default=8, help='Batch size for evaluation')
    parser.add_argument('--max_length', type=int, default=512, help='Maximum sequence length')
    parser.add_argument('--num_samples', type=int, default=1000, help='Number of samples to evaluate')
    parser.add_argument('--device', type=str, default='auto', help='Device to use')
    parser.add_argument('--fp16', action='store_true', help='Use FP16 precision')
    parser.add_argument('--output', type=str, default='benchmark_results.json', help='Output file')
    return parser.parse_args()


def setup_device(device_arg):
    """Setup device for evaluation"""
    if device_arg == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = device_arg
    return device


def load_model_and_tokenizer(model_name, task_type):
    """Load model and tokenizer based on task type"""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    if task_type == 'language_modeling':
        model = AutoModelForCausalLM.from_pretrained(model_name)
    elif task_type == 'classification':
        # Pour la classification, on utilise un dataset simple
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=2
        )
    else:
        raise ValueError(f"Unsupported task type: {task_type}")
    
    return model, tokenizer


def prepare_dataset(dataset_name, tokenizer, task_type, max_length, num_samples):
    """Prepare dataset for evaluation"""
    if task_type == 'language_modeling':
        return prepare_lm_dataset(dataset_name, tokenizer, max_length, num_samples)
    elif task_type == 'classification':
        return prepare_classification_dataset(tokenizer, max_length, num_samples)
    else:
        raise ValueError(f"Unsupported task type: {task_type}")


def prepare_lm_dataset(dataset_name, tokenizer, max_length, num_samples):
    """Prepare language modeling dataset"""
    dataset = load_dataset('wikitext', dataset_name)
    
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            max_length=max_length,
            padding='max_length',
            return_tensors=None
        )
    
    tokenized_dataset = dataset.map(
        tokenize_function, 
        batched=True, 
        remove_columns=['text']
    )
    
    # Take subset for evaluation
    eval_dataset = tokenized_dataset['test'].select(range(min(num_samples, len(tokenized_dataset['test']))))
    
    return eval_dataset


def prepare_classification_dataset(tokenizer, max_length, num_samples):
    """Prepare classification dataset (synthetic for demonstration)"""
    # Créer un dataset synthétique simple pour la classification
    texts = [
        "This is a positive example of good content.",
        "This is a negative example of bad content.",
        "I really like this amazing product!",
        "I hate this terrible product!",
        "The weather is beautiful today.",
        "The weather is awful today.",
    ] * (num_samples // 6 + 1)
    
    labels = [1, 0, 1, 0, 1, 0] * (num_samples // 6 + 1)
    
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            max_length=max_length,
            padding='max_length',
            return_tensors=None
        )
    
    dataset_dict = {
        'text': texts[:num_samples],
        'label': labels[:num_samples]
    }
    
    tokenized = tokenize_function(dataset_dict)
    tokenized['labels'] = labels[:num_samples]
    
    return tokenized


def evaluate_language_modeling(model, dataloader, device, accelerator):
    """Evaluate language modeling performance"""
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    perplexities = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating LM"):
            batch = {k: v.to(device) for k, v in batch.items()}
            
            outputs = model(**batch)
            loss = outputs.loss
            
            # Calculate perplexity
            perplexity = torch.exp(loss).item()
            perplexities.append(perplexity)
            
            # Count tokens (excluding padding)
            attention_mask = batch['attention_mask']
            num_tokens = attention_mask.sum().item()
            
            total_loss += loss.item() * num_tokens
            total_tokens += num_tokens
    
    avg_loss = total_loss / total_tokens
    avg_perplexity = np.mean(perplexities)
    
    return {
        'loss': avg_loss,
        'perplexity': avg_perplexity,
        'perplexity_std': np.std(perplexities)
    }


def evaluate_classification(model, dataloader, device, accelerator):
    """Evaluate classification performance"""
    model.eval()
    correct = 0
    total = 0
    predictions = []
    true_labels = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating Classification"):
            batch = {k: v.to(device) for k, v in batch.items()}
            
            outputs = model(**batch)
            logits = outputs.logits
            
            pred = torch.argmax(logits, dim=-1)
            correct += (pred == batch['labels']).sum().item()
            total += batch['labels'].size(0)
            
            predictions.extend(pred.cpu().numpy())
            true_labels.extend(batch['labels'].cpu().numpy())
    
    accuracy = correct / total if total > 0 else 0.0
    
    return {
        'accuracy': accuracy,
        'correct': correct,
        'total': total
    }


def measure_inference_speed(model, dataloader, device, num_runs=10):
    """Measure inference speed"""
    model.eval()
    
    # Warmup
    for batch in list(dataloader)[:2]:
        batch = {k: v.to(device) for k, v in batch.items()}
        with torch.no_grad():
            _ = model(**batch)
    
    # Measure speed
    times = []
    with torch.no_grad():
        for batch in list(dataloader)[:num_runs]:
            batch = {k: v.to(device) for k, v in batch.items()}
            
            if device == 'cuda':
                torch.cuda.synchronize()
            
            start_time = time.time()
            _ = model(**batch)
            
            if device == 'cuda':
                torch.cuda.synchronize()
            
            end_time = time.time()
            times.append(end_time - start_time)
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    
    return {
        'avg_inference_time': avg_time,
        'std_inference_time': std_time,
        'samples_per_second': len(times) / sum(times)
    }


def main():
    args = parse_args()
    
    # Setup
    device = setup_device(args.device)
    accelerator = Accelerator(mixed_precision='fp16' if args.fp16 else 'no')
    
    print(f"Loading model: {args.model}")
    print(f"Task: {args.task}")
    print(f"Device: {device}")
    
    # Load original model
    original_model, tokenizer = load_model_and_tokenizer(args.model, args.task)
    original_model = original_model.to(device)
    
    # Load compressed model
    compressed_model, _ = load_model_and_tokenizer(args.model, args.task)
    recipe = qtc.recipe.load_recipe(args.recipe)
    apply_summary = qtc.apply.apply_recipe_to_model(compressed_model, recipe)
    compressed_model = compressed_model.to(device)
    
    # Prepare dataset
    print(f"Preparing dataset: {args.dataset}")
    dataset = prepare_dataset(
        args.dataset, tokenizer, args.task, 
        args.max_length, args.num_samples
    )
    
    # Create dataloader
    if args.task == 'language_modeling':
        collate_fn = DataCollatorWithPadding(tokenizer=tokenizer)
    else:
        collate_fn = None
    
    dataloader = DataLoader(
        dataset, 
        batch_size=args.batch_size, 
        shuffle=False, 
        collate_fn=collate_fn
    )
    
    # Prepare models with accelerator
    original_model, compressed_model, dataloader = accelerator.prepare(
        original_model, compressed_model, dataloader
    )
    
    # Get model statistics
    original_params = qtc.apply.count_params(original_model)
    compressed_params = qtc.apply.count_params(compressed_model)
    compression_stats = qtc.apply.get_compression_stats(original_model, compressed_model)
    
    print(f"\nModel Statistics:")
    print(f"Original parameters: {original_params:,}")
    print(f"Compressed parameters: {compressed_params:,}")
    print(f"Compression ratio: {compression_stats['compression_ratio']:.2f}x")
    print(f"Memory reduction: {compression_stats['memory_reduction']:.2f}x")
    
    # Evaluate original model
    print(f"\nEvaluating original model...")
    if args.task == 'language_modeling':
        original_metrics = evaluate_language_modeling(
            original_model, dataloader, device, accelerator
        )
    else:
        original_metrics = evaluate_classification(
            original_model, dataloader, device, accelerator
        )
    
    original_speed = measure_inference_speed(original_model, dataloader, device)
    
    # Evaluate compressed model
    print(f"\nEvaluating compressed model...")
    if args.task == 'language_modeling':
        compressed_metrics = evaluate_language_modeling(
            compressed_model, dataloader, device, accelerator
        )
    else:
        compressed_metrics = evaluate_classification(
            compressed_model, dataloader, device, accelerator
        )
    
    compressed_speed = measure_inference_speed(compressed_model, dataloader, device)
    
    # Calculate performance degradation
    if args.task == 'language_modeling':
        perplexity_degradation = (
            compressed_metrics['perplexity'] - original_metrics['perplexity']
        ) / original_metrics['perplexity'] * 100
        loss_degradation = (
            compressed_metrics['loss'] - original_metrics['loss']
        ) / original_metrics['loss'] * 100
    else:
        accuracy_degradation = (
            original_metrics['accuracy'] - compressed_metrics['accuracy']
        ) * 100
    
    # Compile results
    results = {
        'model': args.model,
        'recipe': args.recipe,
        'task': args.task,
        'dataset': args.dataset,
        'compression_stats': compression_stats,
        'original_model': {
            'parameters': original_params,
            'metrics': original_metrics,
            'speed': original_speed
        },
        'compressed_model': {
            'parameters': compressed_params,
            'metrics': compressed_metrics,
            'speed': compressed_speed
        },
        'degradation': {}
    }
    
    if args.task == 'language_modeling':
        results['degradation'] = {
            'perplexity_degradation_percent': perplexity_degradation,
            'loss_degradation_percent': loss_degradation
        }
    else:
        results['degradation'] = {
            'accuracy_degradation_percent': accuracy_degradation
        }
    
    # Print results
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS")
    print(f"{'='*60}")
    
    print(f"\nCompression:")
    print(f"  Parameters: {original_params:,} → {compressed_params:,}")
    print(f"  Compression ratio: {compression_stats['compression_ratio']:.2f}x")
    print(f"  Memory reduction: {compression_stats['memory_reduction']:.2f}x")
    
    print(f"\nPerformance Metrics:")
    if args.task == 'language_modeling':
        print(f"  Perplexity: {original_metrics['perplexity']:.2f} → {compressed_metrics['perplexity']:.2f}")
        print(f"  Loss: {original_metrics['loss']:.4f} → {compressed_metrics['loss']:.4f}")
        print(f"  Perplexity degradation: {perplexity_degradation:+.2f}%")
        print(f"  Loss degradation: {loss_degradation:+.2f}%")
    else:
        print(f"  Accuracy: {original_metrics['accuracy']:.4f} → {compressed_metrics['accuracy']:.4f}")
        print(f"  Accuracy degradation: {accuracy_degradation:+.2f}%")
    
    print(f"\nSpeed:")
    print(f"  Original: {original_speed['avg_inference_time']:.4f}s ± {original_speed['std_inference_time']:.4f}s")
    print(f"  Compressed: {compressed_speed['avg_inference_time']:.4f}s ± {compressed_speed['std_inference_time']:.4f}s")
    print(f"  Speed ratio: {original_speed['avg_inference_time'] / compressed_speed['avg_inference_time']:.2f}x")
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {args.output}")
    
    # Summary judgment
    print(f"\n{'='*60}")
    print(f"SUMMARY JUDGMENT")
    print(f"{'='*60}")
    
    if args.task == 'language_modeling':
        if perplexity_degradation < 5:
            print(f"✅ EXCELLENT: Perplexity degradation < 5% ({perplexity_degradation:.2f}%)")
        elif perplexity_degradation < 15:
            print(f"🟡 GOOD: Perplexity degradation < 15% ({perplexity_degradation:.2f}%)")
        elif perplexity_degradation < 30:
            print(f"🟠 ACCEPTABLE: Perplexity degradation < 30% ({perplexity_degradation:.2f}%)")
        else:
            print(f"❌ POOR: Perplexity degradation > 30% ({perplexity_degradation:.2f}%)")
    else:
        if accuracy_degradation < 2:
            print(f"✅ EXCELLENT: Accuracy degradation < 2% ({accuracy_degradation:.2f}%)")
        elif accuracy_degradation < 5:
            print(f"🟡 GOOD: Accuracy degradation < 5% ({accuracy_degradation:.2f}%)")
        elif accuracy_degradation < 10:
            print(f"🟠 ACCEPTABLE: Accuracy degradation < 10% ({accuracy_degradation:.2f}%)")
        else:
            print(f"❌ POOR: Accuracy degradation > 10% ({accuracy_degradation:.2f}%)")
    
    if compression_stats['compression_ratio'] > 5:
        print(f"✅ HIGH COMPRESSION: {compression_stats['compression_ratio']:.1f}x")
    elif compression_stats['compression_ratio'] > 2:
        print(f"🟡 MODERATE COMPRESSION: {compression_stats['compression_ratio']:.1f}x")
    else:
        print(f"🟠 LOW COMPRESSION: {compression_stats['compression_ratio']:.1f}x")


if __name__ == '__main__':
    main() 