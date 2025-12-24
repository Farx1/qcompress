#!/usr/bin/env python3
"""
Script de benchmark basique pour tester la compression TT sur des couches isolées.
"""

import os
import sys
import argparse
import json
import time
import torch
import numpy as np
from torch import nn

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Imports directs
import tn.tt_layers


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark basique de compression TT")
    parser.add_argument('--output', type=str, default='benchmark_basic_results.json', help='Output file')
    return parser.parse_args()


def test_tt_linear_compression():
    """Test de compression avec TTLinear"""
    print("Testing TTLinear compression...")
    
    # Paramètres de test
    in_features = 768
    out_features = 3072
    batch_size = 32
    
    # Créer une couche dense originale
    dense_layer = nn.Linear(in_features, out_features)
    
    # Créer une couche TT équivalente
    in_modes = [16, 16, 3]  # 768 = 16*16*3
    out_modes = [64, 12, 4]  # 3072 = 64*12*4
    ranks = [1, 16, 16, 1]
    
    tt_layer = tn.tt_layers.TTLinear(
        in_modes=in_modes,
        out_modes=out_modes,
        ranks=ranks,
        bias=True,
        use_dense_path=True
    )
    
    # Données de test
    x = torch.randn(batch_size, in_features)
    
    # Mesurer les performances
    print(f"Input shape: {x.shape}")
    print(f"Dense layer parameters: {sum(p.numel() for p in dense_layer.parameters()):,}")
    print(f"TT layer parameters: {sum(p.numel() for p in tt_layer.parameters()):,}")
    
    # Test de forward pass
    print("\nTesting forward pass...")
    
    # Dense layer
    dense_layer.eval()
    with torch.no_grad():
        start_time = time.time()
        for _ in range(10):
            y_dense = dense_layer(x)
        dense_time = (time.time() - start_time) / 10
    
    # TT layer
    tt_layer.eval()
    with torch.no_grad():
        start_time = time.time()
        for _ in range(10):
            y_tt = tt_layer(x)
        tt_time = (time.time() - start_time) / 10
    
    # Comparer les résultats
    print(f"Dense output shape: {y_dense.shape}")
    print(f"TT output shape: {y_tt.shape}")
    print(f"Dense forward time: {dense_time:.6f}s")
    print(f"TT forward time: {tt_time:.6f}s")
    print(f"Speed ratio: {dense_time / tt_time:.2f}x")
    
    # Calculer la compression
    dense_params = sum(p.numel() for p in dense_layer.parameters())
    tt_params = sum(p.numel() for p in tt_layer.parameters())
    compression_ratio = dense_params / tt_params
    
    print(f"Compression ratio: {compression_ratio:.2f}x")
    
    return {
        'dense_params': dense_params,
        'tt_params': tt_params,
        'compression_ratio': compression_ratio,
        'dense_time': dense_time,
        'tt_time': tt_time,
        'speed_ratio': dense_time / tt_time
    }


def test_tt_embedding_compression():
    """Test de compression avec TTEmbedding"""
    print("\nTesting TTEmbedding compression...")
    
    # Paramètres de test
    num_embeddings = 50257
    embedding_dim = 768
    batch_size = 32
    seq_len = 64
    
    # Créer une couche d'embedding dense originale
    dense_embedding = nn.Embedding(num_embeddings, embedding_dim)
    
    # Créer une couche TT équivalente avec des dimensions qui correspondent
    in_modes = [17, 17, 17]  # 4913 ≈ 50257/10
    out_modes = [16, 16, 3]  # 768 = 16*16*3
    ranks = [1, 16, 16, 1]  # 4 rangs pour 3 modes
    
    tt_embedding = tn.tt_layers.TTEmbedding(
        in_modes=in_modes,
        out_modes=out_modes,
        ranks=ranks,
        use_dense_path=True
    )
    
    # Données de test
    input_ids = torch.randint(0, min(num_embeddings, 4913), (batch_size, seq_len))
    
    # Mesurer les performances
    print(f"Input shape: {input_ids.shape}")
    print(f"Dense embedding parameters: {sum(p.numel() for p in dense_embedding.parameters()):,}")
    print(f"TT embedding parameters: {sum(p.numel() for p in tt_embedding.parameters()):,}")
    
    # Test de forward pass
    print("\nTesting forward pass...")
    
    # Dense embedding
    dense_embedding.eval()
    with torch.no_grad():
        start_time = time.time()
        for _ in range(10):
            y_dense = dense_embedding(input_ids)
        dense_time = (time.time() - start_time) / 10
    
    # TT embedding
    tt_embedding.eval()
    with torch.no_grad():
        start_time = time.time()
        for _ in range(10):
            y_tt = tt_embedding(input_ids)
        tt_time = (time.time() - start_time) / 10
    
    # Comparer les résultats
    print(f"Dense output shape: {y_dense.shape}")
    print(f"TT output shape: {y_tt.shape}")
    print(f"Dense forward time: {dense_time:.6f}s")
    print(f"TT forward time: {tt_time:.6f}s")
    print(f"Speed ratio: {dense_time / tt_time:.2f}x")
    
    # Calculer la compression
    dense_params = sum(p.numel() for p in dense_embedding.parameters())
    tt_params = sum(p.numel() for p in tt_embedding.parameters())
    compression_ratio = dense_params / tt_params
    
    print(f"Compression ratio: {compression_ratio:.2f}x")
    
    return {
        'dense_params': dense_params,
        'tt_params': tt_params,
        'compression_ratio': compression_ratio,
        'dense_time': dense_time,
        'tt_time': tt_time,
        'speed_ratio': dense_time / tt_time
    }


def main():
    args = parse_args()
    
    print("🧪 Benchmark basique de compression TT")
    print("=" * 50)
    
    # Test TTLinear
    linear_results = test_tt_linear_compression()
    
    # Test TTEmbedding
    embedding_results = test_tt_embedding_compression()
    
    # Compiler les résultats
    results = {
        'linear_compression': linear_results,
        'embedding_compression': embedding_results,
        'summary': {
            'avg_compression_ratio': (linear_results['compression_ratio'] + embedding_results['compression_ratio']) / 2,
            'avg_speed_ratio': (linear_results['speed_ratio'] + embedding_results['speed_ratio']) / 2
        }
    }
    
    # Afficher le résumé
    print(f"\n{'='*60}")
    print(f"RÉSUMÉ DES RÉSULTATS")
    print(f"{'='*60}")
    
    print(f"\nCompression:")
    print(f"  Linear: {linear_results['compression_ratio']:.2f}x")
    print(f"  Embedding: {embedding_results['compression_ratio']:.2f}x")
    print(f"  Moyenne: {results['summary']['avg_compression_ratio']:.2f}x")
    
    print(f"\nPerformance:")
    print(f"  Linear: {linear_results['speed_ratio']:.2f}x")
    print(f"  Embedding: {embedding_results['speed_ratio']:.2f}x")
    print(f"  Moyenne: {results['summary']['avg_speed_ratio']:.2f}x")
    
    # Jugement
    print(f"\n{'='*60}")
    print(f"JUGEMENT")
    print(f"{'='*60}")
    
    avg_compression = results['summary']['avg_compression_ratio']
    avg_speed = results['summary']['avg_speed_ratio']
    
    if avg_compression > 5:
        print(f"✅ EXCELLENTE COMPRESSION: {avg_compression:.1f}x")
    elif avg_compression > 2:
        print(f"🟡 BONNE COMPRESSION: {avg_compression:.1f}x")
    else:
        print(f"🟠 COMPRESSION FAIBLE: {avg_compression:.1f}x")
    
    if avg_speed > 1.5:
        print(f"✅ RAPIDE: {avg_speed:.1f}x plus rapide")
    elif avg_speed > 0.8:
        print(f"🟡 ACCEPTABLE: {avg_speed:.1f}x")
    else:
        print(f"🟠 LENT: {avg_speed:.1f}x")
    
    # Sauvegarder les résultats
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nRésultats sauvegardés dans: {args.output}")


if __name__ == '__main__':
    main() 