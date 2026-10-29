import torch
import pytest
import numpy as np
from src.tn.tt_layers import tt_svd_init_from_dense, TTLinear, TTEmbedding, _contract_cores


def test_tt_svd_init_basic():
    """Test de base de l'initialisation TT-SVD."""
    # Création d'un poids dense
    W = torch.randn(16, 16)
    in_modes = [4, 4]
    out_modes = [4, 4]
    ranks = [1, 2, 1]
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Vérifications de base
    assert len(cores) == 2
    assert cores[0].shape == (1, 4, 4, 2)
    assert cores[1].shape == (2, 4, 4, 1)
    
    # Vérification que les cores sont des tenseurs PyTorch
    for core in cores:
        assert isinstance(core, torch.Tensor)


def test_tt_svd_init_reconstruction():
    """Test de la reconstruction après TT-SVD."""
    # Création d'un poids dense
    W = torch.randn(16, 16)
    in_modes = [4, 4]
    out_modes = [4, 4]
    ranks = [1, 16, 1]  # Rang plein: max rank of the (m1*n1, m2*n2) unfolding
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    W_reconstructed = _contract_cores(cores).reshape(16, 16)
    
    # Calcul de l'erreur de reconstruction
    reconstruction_error = torch.norm(W - W_reconstructed) / torch.norm(W)
    
    print(f"Erreur de reconstruction: {reconstruction_error:.6f}")
    
    # Rang plein: reconstruction exacte
    assert reconstruction_error < 1e-5, f"Erreur de reconstruction trop élevée: {reconstruction_error}"


def test_tt_svd_init_embedding():
    """Test de l'initialisation TT-SVD pour les embeddings."""
    # Création d'un poids d'embedding
    vocab_size = 16
    embedding_dim = 8
    W = torch.randn(embedding_dim, vocab_size)  # (dim, vocab)
    
    in_modes = [4, 4]  # Facteurs de vocab_size
    out_modes = [2, 4]  # Facteurs de embedding_dim
    ranks = [1, 3, 1]
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Vérifications
    assert len(cores) == 2
    assert cores[0].shape == (1, 2, 4, 3)
    assert cores[1].shape == (3, 4, 4, 1)


def test_tt_svd_init_ranks():
    """Test avec différents rangs."""
    W = torch.randn(16, 16)
    in_modes = [4, 4]
    out_modes = [4, 4]
    
    # Test avec différents rangs
    rank_configs = [
        [1, 1, 1],  # Rang minimal
        [1, 2, 1],  # Rang intermédiaire
        [1, 4, 1],  # Rang élevé
        [1, 8, 1],  # Rang très élevé
    ]
    
    for ranks in rank_configs:
        cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
        
        # Vérification des formes
        assert cores[0].shape == (1, 4, 4, ranks[1])
        assert cores[1].shape == (ranks[1], 4, 4, 1)


def test_tt_svd_init_tt_layer():
    """Test de l'initialisation TT-SVD dans une couche TT."""
    # Création d'un poids dense
    W = torch.randn(16, 16)
    in_modes = [4, 4]
    out_modes = [4, 4]
    ranks = [1, 4, 1]
    
    # Création de la couche TT
    layer = TTLinear(in_modes, out_modes, ranks)
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Copie des cores dans la couche
    with torch.no_grad():
        for i, core in enumerate(cores):
            layer.cores[i].copy_(core)
    
    # Test du forward
    x = torch.randn(2, 16)
    y = layer(x)
    assert y.shape == (2, 16)


def test_tt_svd_init_error_handling():
    """Test de la gestion d'erreurs."""
    W = torch.randn(16, 16)
    
    # Test avec des modes incompatibles
    with pytest.raises(AssertionError):
        tt_svd_init_from_dense(W, [4, 4], [4], [1, 2, 1])
    
    # Test avec des rangs incompatibles
    with pytest.raises(AssertionError):
        tt_svd_init_from_dense(W, [4, 4], [4, 4], [1, 2])
    
    # Test avec des rangs aux extrémités incorrects
    with pytest.raises(AssertionError):
        tt_svd_init_from_dense(W, [4, 4], [4, 4], [2, 2, 1])


def test_tt_svd_init_vs_random():
    """Comparaison TT-SVD vs initialisation aléatoire."""
    W = torch.randn(16, 16)
    in_modes = [4, 4]
    out_modes = [4, 4]
    ranks = [1, 4, 1]
    
    # Initialisation TT-SVD
    cores_svd = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Création de couches TT
    layer_svd = TTLinear(in_modes, out_modes, ranks)
    layer_random = TTLinear(in_modes, out_modes, ranks)
    
    # Copie des cores SVD
    with torch.no_grad():
        for i, core in enumerate(cores_svd):
            layer_svd.cores[i].copy_(core)
    
    # Test de reconstruction
    W_svd = layer_svd.reconstruct_weight()
    W_random = layer_random.reconstruct_weight()
    
    # Calcul des erreurs
    error_svd = torch.norm(W - W_svd) / torch.norm(W)
    error_random = torch.norm(W - W_random) / torch.norm(W)
    
    print(f"Erreur TT-SVD: {error_svd:.6f}")
    print(f"Erreur aléatoire: {error_random:.6f}")
    
    # TT-SVD devrait avoir une erreur plus faible
    assert error_svd < error_random, f"TT-SVD pas meilleur que aléatoire: {error_svd} vs {error_random}"


def test_tt_svd_init_large_matrix():
    """Test avec une matrice plus grande."""
    # Matrice plus grande pour tester la robustesse
    W = torch.randn(64, 64)
    in_modes = [8, 8]
    out_modes = [8, 8]
    ranks = [1, 64, 1]  # Rang plein
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Vérifications
    assert len(cores) == 2
    assert cores[0].shape == (1, 8, 8, 64)
    assert cores[1].shape == (64, 8, 8, 1)
    
    W_reconstructed = _contract_cores(cores).reshape(64, 64)
    
    reconstruction_error = torch.norm(W - W_reconstructed) / torch.norm(W)
    print(f"Erreur de reconstruction (64x64): {reconstruction_error:.6f}")
    
    assert reconstruction_error < 1e-5, f"Erreur trop élevée pour matrice 64x64: {reconstruction_error}"



def test_tt_svd_d3_full_rank():
    """d=3, ranks at the unfolding maxima: exact, and loaded into TTLinear."""
    W = torch.randn(24, 12)  # out = 2*3*4, in = 3*2*2
    in_modes, out_modes, ranks = [3, 2, 2], [2, 3, 4], [1, 6, 8, 1]
    layer = TTLinear(in_modes, out_modes, ranks)
    with torch.no_grad():
        for core, c in zip(layer.cores, tt_svd_init_from_dense(W, in_modes, out_modes, ranks)):
            core.copy_(c)
    assert torch.norm(W - layer.reconstruct_weight()) / torch.norm(W) < 1e-5


def test_tt_svd_truncated_error_decreases_with_rank():
    W = torch.randn(64, 64)
    errors = []
    for r in [1, 4, 16, 64]:
        cores = tt_svd_init_from_dense(W, [8, 8], [8, 8], [1, r, 1])
        errors.append((torch.norm(W - _contract_cores(cores).reshape(64, 64)) / torch.norm(W)).item())
    assert all(a > b for a, b in zip(errors, errors[1:])), errors
    assert errors[-1] < 1e-5


def test_contract_cores_alphabet_guard():
    cores = [torch.ones(1, 1, 1, 1) for _ in range(9)]  # 3*9+1 = 28 > 26 letters
    with pytest.raises(ValueError):
        _contract_cores(cores)
    assert _contract_cores(cores[:8]).numel() == 1  # 3*8+1 = 25 fits


if __name__ == '__main__':
    pytest.main([__file__]) 