import torch
import time
import pytest
from src.tn.tt_layers import TTLinear, TTEmbedding


def benchmark_forward(layer, input_data, num_runs=100, warmup_runs=10):
    """
    Benchmark du forward pass d'une couche.
    
    Args:
        layer: Couche à benchmarker
        input_data: Données d'entrée
        num_runs: Nombre de runs pour la moyenne
        warmup_runs: Nombre de runs de warmup
        
    Returns:
        Temps moyen en secondes
    """
    layer.eval()
    
    # Warmup
    with torch.no_grad():
        for _ in range(warmup_runs):
            _ = layer(input_data)
    
    # Synchronisation GPU si nécessaire
    if input_data.device.type == 'cuda':
        torch.cuda.synchronize()
    
    # Mesures
    times = []
    with torch.no_grad():
        for _ in range(num_runs):
            if input_data.device.type == 'cuda':
                torch.cuda.synchronize()
            
            start_time = time.time()
            _ = layer(input_data)
            
            if input_data.device.type == 'cuda':
                torch.cuda.synchronize()
            
            end_time = time.time()
            times.append(end_time - start_time)
    
    return sum(times) / len(times)


def test_tt_linear_speed_vs_dense():
    """Test de performance TT Linear vs Dense."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Configuration
    in_features = 768
    out_features = 3072
    batch_size = 32
    seq_len = 512
    
    # Création des couches
    tt_layer = TTLinear(
        in_modes=[16, 16, 3],  # 768
        out_modes=[64, 12, 4],  # 3072
        ranks=[1, 16, 16, 1],
        use_dense_path=False
    ).to(device)
    
    dense_layer = torch.nn.Linear(in_features, out_features).to(device)
    
    # Données d'entrée
    x = torch.randn(batch_size, seq_len, in_features).to(device)
    
    # Benchmark TT
    tt_time = benchmark_forward(tt_layer, x)
    
    # Benchmark Dense
    dense_time = benchmark_forward(dense_layer, x)
    
    print(f"\nBenchmark TT Linear vs Dense:")
    print(f"Input shape: {x.shape}")
    print(f"TT time: {tt_time*1000:.2f}ms")
    print(f"Dense time: {dense_time*1000:.2f}ms")
    print(f"Speedup: {dense_time/tt_time:.2f}x")
    
    # Vérification que TT n'est pas trop lent (tolérance de 10x)
    assert tt_time < dense_time * 10, f"TT trop lent: {tt_time:.4f}s vs {dense_time:.4f}s"


def test_tt_linear_efficient_vs_dense_path():
    """Test de performance chemin efficace vs dense path."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Configuration
    in_features = 256
    out_features = 512
    batch_size = 16
    
    # Création des couches
    tt_efficient = TTLinear(
        in_modes=[16, 16],  # 256
        out_modes=[16, 32],  # 512
        ranks=[1, 8, 1],
        use_dense_path=False
    ).to(device)
    
    tt_dense_path = TTLinear(
        in_modes=[16, 16],  # 256
        out_modes=[16, 32],  # 512
        ranks=[1, 8, 1],
        use_dense_path=True
    ).to(device)
    
    # Données d'entrée
    x = torch.randn(batch_size, in_features).to(device)
    
    # Benchmark
    efficient_time = benchmark_forward(tt_efficient, x)
    dense_path_time = benchmark_forward(tt_dense_path, x)
    
    print(f"\nBenchmark TT Efficient vs Dense Path:")
    print(f"Input shape: {x.shape}")
    print(f"Efficient time: {efficient_time*1000:.2f}ms")
    print(f"Dense path time: {dense_path_time*1000:.2f}ms")
    print(f"Speedup: {dense_path_time/efficient_time:.2f}x")
    
    # Vérification que le chemin efficace est plus rapide
    assert efficient_time < dense_path_time, f"Chemin efficace plus lent: {efficient_time:.4f}s vs {dense_path_time:.4f}s"


def test_tt_embedding_speed():
    """Test de performance TT Embedding."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Configuration
    vocab_size = 50257
    embedding_dim = 768
    batch_size = 32
    seq_len = 512
    
    # Création des couches
    tt_embedding = TTEmbedding(
        in_modes=[17, 17, 17, 10],  # ≈ 50257
        out_modes=[16, 16, 3],  # 768
        ranks=[1, 16, 16, 1],
        use_dense_path=False
    ).to(device)
    
    dense_embedding = torch.nn.Embedding(vocab_size, embedding_dim).to(device)
    
    # Données d'entrée
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len)).to(device)
    
    # Benchmark TT
    tt_time = benchmark_forward(tt_embedding, input_ids)
    
    # Benchmark Dense
    dense_time = benchmark_forward(dense_embedding, input_ids)
    
    print(f"\nBenchmark TT Embedding vs Dense:")
    print(f"Input shape: {input_ids.shape}")
    print(f"TT time: {tt_time*1000:.2f}ms")
    print(f"Dense time: {dense_time*1000:.2f}ms")
    print(f"Speedup: {dense_time/tt_time:.2f}x")
    
    # Vérification que TT n'est pas trop lent (tolérance de 5x)
    assert tt_time < dense_time * 5, f"TT trop lent: {tt_time:.4f}s vs {dense_time:.4f}s"


def test_memory_usage():
    """Test de l'utilisation mémoire."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    if device.type == 'cpu':
        pytest.skip("Test mémoire uniquement sur GPU")
    
    # Configuration
    in_features = 768
    out_features = 3072
    batch_size = 32
    seq_len = 512
    
    # Création des couches
    tt_layer = TTLinear(
        in_modes=[16, 16, 3],
        out_modes=[64, 12, 4],
        ranks=[1, 16, 16, 1]
    ).to(device)
    
    dense_layer = torch.nn.Linear(in_features, out_features).to(device)
    
    # Nettoyage mémoire
    torch.cuda.empty_cache()
    
    # Mesure mémoire TT
    torch.cuda.reset_peak_memory_stats()
    x_tt = torch.randn(batch_size, seq_len, in_features).to(device)
    _ = tt_layer(x_tt)
    tt_memory = torch.cuda.max_memory_allocated() / 1024**2  # MB
    
    # Nettoyage
    del x_tt
    torch.cuda.empty_cache()
    
    # Mesure mémoire Dense
    torch.cuda.reset_peak_memory_stats()
    x_dense = torch.randn(batch_size, seq_len, in_features).to(device)
    _ = dense_layer(x_dense)
    dense_memory = torch.cuda.max_memory_allocated() / 1024**2  # MB
    
    print(f"\nUtilisation mémoire:")
    print(f"TT memory: {tt_memory:.1f}MB")
    print(f"Dense memory: {dense_memory:.1f}MB")
    print(f"Memory reduction: {dense_memory/tt_memory:.2f}x")
    
    # Vérification que TT utilise moins de mémoire
    assert tt_memory < dense_memory, f"TT utilise plus de mémoire: {tt_memory:.1f}MB vs {dense_memory:.1f}MB"


def test_gradient_memory():
    """Test de l'utilisation mémoire avec gradients."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    if device.type == 'cpu':
        pytest.skip("Test mémoire uniquement sur GPU")
    
    # Configuration
    in_features = 256
    out_features = 512
    batch_size = 16
    
    # Création des couches
    tt_layer = TTLinear(
        in_modes=[16, 16],
        out_modes=[16, 32],
        ranks=[1, 8, 1]
    ).to(device)
    
    dense_layer = torch.nn.Linear(in_features, out_features).to(device)
    
    # Nettoyage mémoire
    torch.cuda.empty_cache()
    
    # Mesure mémoire TT avec gradients
    torch.cuda.reset_peak_memory_stats()
    x_tt = torch.randn(batch_size, in_features, requires_grad=True).to(device)
    y_tt = tt_layer(x_tt)
    loss_tt = y_tt.sum()
    loss_tt.backward()
    tt_memory = torch.cuda.max_memory_allocated() / 1024**2  # MB
    
    # Nettoyage
    del x_tt, y_tt, loss_tt
    torch.cuda.empty_cache()
    
    # Mesure mémoire Dense avec gradients
    torch.cuda.reset_peak_memory_stats()
    x_dense = torch.randn(batch_size, in_features, requires_grad=True).to(device)
    y_dense = dense_layer(x_dense)
    loss_dense = y_dense.sum()
    loss_dense.backward()
    dense_memory = torch.cuda.max_memory_allocated() / 1024**2  # MB
    
    print(f"\nUtilisation mémoire avec gradients:")
    print(f"TT memory: {tt_memory:.1f}MB")
    print(f"Dense memory: {dense_memory:.1f}MB")
    print(f"Memory reduction: {dense_memory/tt_memory:.2f}x")


if __name__ == '__main__':
    pytest.main([__file__]) 