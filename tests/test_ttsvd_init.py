import torch
import pytest
import numpy as np
from src.tn.tt_layers import tt_svd_init_from_dense, TTLinear, TTEmbedding


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
    ranks = [1, 4, 1]  # Rang plus élevé pour meilleure approximation
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Reconstruction manuelle
    # Contracter les cores pour reconstruire le poids
    import opt_einsum as oe
    
    # Équation de contraction: 'a,m1,n1,b, b,m2,n2,c -> m1,m2,n1,n2'
    eq = 'a,m1,n1,b, b,m2,n2,c -> m1,m2,n1,n2'
    T = oe.contract(eq, cores[0], cores[1])
    
    # Reshape vers la forme originale
    W_reconstructed = T.reshape(16, 16)
    
    # Calcul de l'erreur de reconstruction
    reconstruction_error = torch.norm(W - W_reconstructed) / torch.norm(W)
    
    print(f"Erreur de reconstruction: {reconstruction_error:.6f}")
    
    # L'erreur devrait être faible avec un rang suffisant
    assert reconstruction_error < 0.1, f"Erreur de reconstruction trop élevée: {reconstruction_error}"


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
    ranks = [1, 8, 1]
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Vérifications
    assert len(cores) == 2
    assert cores[0].shape == (1, 8, 8, 8)
    assert cores[1].shape == (8, 8, 8, 1)
    
    # Test de reconstruction
    import opt_einsum as oe
    eq = 'a,m1,n1,b, b,m2,n2,c -> m1,m2,n1,n2'
    T = oe.contract(eq, cores[0], cores[1])
    W_reconstructed = T.reshape(64, 64)
    
    reconstruction_error = torch.norm(W - W_reconstructed) / torch.norm(W)
    print(f"Erreur de reconstruction (64x64): {reconstruction_error:.6f}")
    
    assert reconstruction_error < 0.2, f"Erreur trop élevée pour matrice 64x64: {reconstruction_error}"


if __name__ == '__main__':
    pytest.main([__file__]) 