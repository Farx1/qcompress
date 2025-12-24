#!/usr/bin/env python3
"""
Script de benchmark simplifié pour évaluer l'impact de la compression TT.
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
    DataCollatorWithPadding
)
from accelerate import Accelerator
from tqdm import tqdm

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Imports directs
import yaml
from tn.tt_layers import TTLinear, TTEmbedding
from tn.math_utils import renyi_entropy
from qtc.utils import count_parameters


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark simple de compression TT")
    parser.add_argument('--model', type=str, default='gpt2', help='HuggingFace model name')
    parser.add_argument('--dataset', type=str, default='wikitext-2-raw-v1', help='Dataset for evaluation')
    parser.add_argument('--batch_size', type=int, default=4, help='Batch size for evaluation')
    parser.add_argument('--max_length', type=int, default=128, help='Maximum sequence length')
    parser.add_argument('--num_samples', type=int, default=100, help='Number of samples to evaluate')
    parser.add_argument('--device', type=str, default='auto', help='Device to use')
    parser.add_argument('--output', type=str, default='benchmark_simple_results.json', help='Output file')
    return parser.parse_args()


def setup_device(device_arg):
    """Setup device for evaluation"""
    if device_arg == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = device_arg
    return device


def prepare_dataset(dataset_name, tokenizer, max_length, num_samples):
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


def measure_inference_speed(model, dataloader, device, num_runs=5):
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


def create_compressed_model(model, compression_ratio=0.5):
    """Create a compressed version of the model by replacing some layers with TT layers"""
    compressed_model = type(model)()
    
    # Copy all attributes
    for name, value in model.__dict__.items():
        if name != '_modules':
            setattr(compressed_model, name, value)
    
    # Copy modules, replacing some with TT versions
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and 'lm_head' in name:
            # Replace lm_head with TT version
            in_features = module.in_features
            out_features = module.out_features
            
            # Simple factorization
            in_modes = [16, 16, 3]  # 768 = 16*16*3
            out_modes = [17, 17, 17, 10]  # ~50257
            ranks = [1, 16, 16, 1]
            
            tt_layer = TTLinear(
                in_modes=in_modes,
                out_modes=out_modes,
                ranks=ranks,
                bias=(module.bias is not None),
                use_dense_path=True  # Use dense path for simplicity
            )
            
            # Set the TT layer
            parent_name = '.'.join(name.split('.')[:-1])
            child_name = name.split('.')[-1]
            
            if parent_name:
                parent = compressed_model.get_submodule(parent_name)
                setattr(parent, child_name, tt_layer)
            else:
                setattr(compressed_model, child_name, tt_layer)
            
            print(f"Replaced {name} with TT layer")
            break
    
    return compressed_model


def main():
    args = parse_args()
    
    # Setup
    device = setup_device(args.device)
    accelerator = Accelerator(mixed_precision='no')
    
    print(f"Loading model: {args.model}")
    print(f"Device: {device}")
    
    # Load original model
    original_model = AutoModelForCausalLM.from_pretrained(args.model)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    original_model = original_model.to(device)
    
    # Create compressed model
    print("Creating compressed model...")
    compressed_model = create_compressed_model(original_model)
    compressed_model = compressed_model.to(device)
    
    # Prepare dataset
    print(f"Preparing dataset: {args.dataset}")
    dataset = prepare_dataset(
        args.dataset, tokenizer, args.max_length, args.num_samples
    )
    
    # Create dataloader
    collate_fn = DataCollatorWithPadding(tokenizer=tokenizer)
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
    original_params = count_parameters(original_model)
    compressed_params = count_parameters(compressed_model)
    compression_ratio = original_params / compressed_params if compressed_params > 0 else 1.0
    
    print(f"\nModel Statistics:")
    print(f"Original parameters: {original_params:,}")
    print(f"Compressed parameters: {compressed_params:,}")
    print(f"Compression ratio: {compression_ratio:.2f}x")
    
    # Evaluate original model
    print(f"\nEvaluating original model...")
    original_metrics = evaluate_language_modeling(
        original_model, dataloader, device, accelerator
    )
    original_speed = measure_inference_speed(original_model, dataloader, device)
    
    # Evaluate compressed model
    print(f"\nEvaluating compressed model...")
    compressed_metrics = evaluate_language_modeling(
        compressed_model, dataloader, device, accelerator
    )
    compressed_speed = measure_inference_speed(compressed_model, dataloader, device)
    
    # Calculate performance degradation
    perplexity_degradation = (
        compressed_metrics['perplexity'] - original_metrics['perplexity']
    ) / original_metrics['perplexity'] * 100
    loss_degradation = (
        compressed_metrics['loss'] - original_metrics['loss']
    ) / original_metrics['loss'] * 100
    
    # Compile results
    results = {
        'model': args.model,
        'dataset': args.dataset,
        'compression_ratio': compression_ratio,
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
        'degradation': {
            'perplexity_degradation_percent': perplexity_degradation,
            'loss_degradation_percent': loss_degradation
        }
    }
    
    # Print results
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS")
    print(f"{'='*60}")
    
    print(f"\nCompression:")
    print(f"  Parameters: {original_params:,} → {compressed_params:,}")
    print(f"  Compression ratio: {compression_ratio:.2f}x")
    
    print(f"\nPerformance Metrics:")
    print(f"  Perplexity: {original_metrics['perplexity']:.2f} → {compressed_metrics['perplexity']:.2f}")
    print(f"  Loss: {original_metrics['loss']:.4f} → {compressed_metrics['loss']:.4f}")
    print(f"  Perplexity degradation: {perplexity_degradation:+.2f}%")
    print(f"  Loss degradation: {loss_degradation:+.2f}%")
    
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
    
    if perplexity_degradation < 5:
        print(f"✅ EXCELLENT: Perplexity degradation < 5% ({perplexity_degradation:.2f}%)")
    elif perplexity_degradation < 15:
        print(f"🟡 GOOD: Perplexity degradation < 15% ({perplexity_degradation:.2f}%)")
    elif perplexity_degradation < 30:
        print(f"🟠 ACCEPTABLE: Perplexity degradation < 30% ({perplexity_degradation:.2f}%)")
    else:
        print(f"❌ POOR: Perplexity degradation > 30% ({perplexity_degradation:.2f}%)")
    
    if compression_ratio > 5:
        print(f"✅ HIGH COMPRESSION: {compression_ratio:.1f}x")
    elif compression_ratio > 2:
        print(f"🟡 MODERATE COMPRESSION: {compression_ratio:.1f}x")
    else:
        print(f"🟠 LOW COMPRESSION: {compression_ratio:.1f}x")


if __name__ == '__main__':
    main() 