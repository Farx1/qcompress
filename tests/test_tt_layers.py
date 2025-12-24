import torch
import pytest
from src.tn.tt_layers import TTLinear, TTEmbedding, tt_svd_init_from_dense


def test_tt_linear_shapes():
    """Test des formes des couches TT Linear."""
    layer = TTLinear([4, 4], [4, 4], [1, 2, 1])
    x = torch.randn(2, 16)
    y = layer(x)
    assert y.shape == (2, 16)


def test_tt_linear_gradients():
    """Test que les gradients passent correctement."""
    layer = TTLinear([4, 4], [4, 4], [1, 2, 1])
    x = torch.randn(2, 16, requires_grad=True)
    y = layer(x)
    loss = y.sum()
    loss.backward()
    
    # Vérification que les gradients sont calculés
    assert x.grad is not None
    for core in layer.cores:
        assert core.grad is not None


def test_tt_linear_dense_path():
    """Test du chemin dense pour debugging."""
    layer = TTLinear([4, 4], [4, 4], [1, 2, 1], use_dense_path=True)
    x = torch.randn(2, 16)
    y = layer(x)
    assert y.shape == (2, 16)


def test_tt_embedding_shapes():
    """Test des formes des couches TT Embedding."""
    layer = TTEmbedding([4, 4], [4, 4], [1, 2, 1])
    input_ids = torch.randint(0, 16, (2, 3))
    y = layer(input_ids)
    assert y.shape == (2, 3, 16)


def test_tt_embedding_gradients():
    """Test que les gradients passent correctement pour les embeddings."""
    layer = TTEmbedding([4, 4], [4, 4], [1, 2, 1])
    input_ids = torch.randint(0, 16, (2, 3))
    y = layer(input_ids)
    loss = y.sum()
    loss.backward()
    
    # Vérification que les gradients sont calculés
    for core in layer.cores:
        assert core.grad is not None


def test_tt_embedding_dense_path():
    """Test du chemin dense pour debugging des embeddings."""
    layer = TTEmbedding([4, 4], [4, 4], [1, 2, 1], use_dense_path=True)
    input_ids = torch.randint(0, 16, (2, 3))
    y = layer(input_ids)
    assert y.shape == (2, 3, 16)


def test_weight_reconstruction():
    """Test de la reconstruction des poids."""
    layer = TTLinear([4, 4], [4, 4], [1, 2, 1])
    W = layer.reconstruct_weight()
    assert W.shape == (16, 16)


def test_tt_svd_init():
    """Test de l'initialisation TT-SVD."""
    # Création d'un poids dense
    W = torch.randn(16, 16)
    in_modes = [4, 4]
    out_modes = [4, 4]
    ranks = [1, 2, 1]
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Vérifications
    assert len(cores) == 2  # 2 cores pour 2 modes
    assert cores[0].shape == (1, 4, 4, 2)  # Premier core
    assert cores[1].shape == (2, 4, 4, 1)  # Deuxième core


def test_tt_svd_init_embedding():
    """Test de l'initialisation TT-SVD pour les embeddings."""
    # Création d'un poids d'embedding
    W = torch.randn(16, 8)  # (vocab_size, embedding_dim)
    in_modes = [4, 4]
    out_modes = [2, 4]
    ranks = [1, 2, 1]
    
    # Initialisation TT-SVD
    cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
    
    # Vérifications
    assert len(cores) == 2
    assert cores[0].shape == (1, 2, 4, 2)
    assert cores[1].shape == (2, 4, 4, 1)


def test_invalid_ranks():
    """Test que des rangs invalides lèvent des erreurs."""
    with pytest.raises(AssertionError):
        TTLinear([4, 4], [4, 4], [1, 2])  # Rangs trop courts
    
    with pytest.raises(AssertionError):
        TTLinear([4, 4], [4, 4], [2, 2, 1])  # r0 != 1
    
    with pytest.raises(AssertionError):
        TTLinear([4, 4], [4, 4], [1, 2, 2])  # rd != 1


def test_invalid_modes():
    """Test que des modes invalides lèvent des erreurs."""
    with pytest.raises(AssertionError):
        TTLinear([4, 4], [4], [1, 2, 1])  # Modes de longueurs différentes


def test_tt_linear_bias():
    """Test que le bias fonctionne correctement."""
    layer = TTLinear([4, 4], [4, 4], [1, 2, 1], bias=True)
    x = torch.randn(2, 16)
    y = layer(x)
    assert y.shape == (2, 16)
    assert layer.bias is not None
    
    # Test sans bias
    layer_no_bias = TTLinear([4, 4], [4, 4], [1, 2, 1], bias=False)
    y_no_bias = layer_no_bias(x)
    assert y_no_bias.shape == (2, 16)
    assert layer_no_bias.bias is None


if __name__ == '__main__':
    pytest.main([__file__]) 