from typing import Dict
import torch
from torch import nn
from .recipe import Recipe, Target
from .utils import expand_paths, get_module, set_module, count_parameters
from src.tn.tt_layers import TTLinear, TTEmbedding, tt_svd_init_from_dense
from src.tn.penalties import attach_penalty_to_module


def count_params(model: nn.Module) -> int:
    """
    Count total parameters in a model.
    
    Args:
        model: PyTorch model
    
    Returns:
        Total parameter count
    """
    return count_parameters(model)


def make_tt_module_from_dense(
    dense: nn.Module, 
    in_modes: list, 
    out_modes: list, 
    ranks: list, 
    init: str = 'random'
) -> nn.Module:
    """
    Create a TT module from a dense module.
    
    Args:
        dense: Dense module (nn.Linear or nn.Embedding)
        in_modes: Input mode dimensions
        out_modes: Output mode dimensions
        ranks: TT ranks
        init: Initialization method ('random', 'ttsvd', 'copy')
    
    Returns:
        TT module (TTLinear or TTEmbedding)
    """
    if isinstance(dense, nn.Embedding):
        mod = TTEmbedding(in_modes=in_modes, out_modes=out_modes, ranks=ranks)
        if init == 'copy':
            mod.copy_from_dense(dense)
        elif init == 'ttsvd':
            # Initialize with TT-SVD
            W = dense.weight.detach()  # (num_embeddings, embedding_dim)
            cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
            with torch.no_grad():
                for i, core in enumerate(cores):
                    mod.cores[i].data.copy_(core)
        return mod
    elif isinstance(dense, nn.Linear):
        mod = TTLinear(
            in_modes=in_modes, 
            out_modes=out_modes, 
            ranks=ranks, 
            bias=(dense.bias is not None)
        )
        if init == 'copy':
            mod.copy_from_dense(dense)
        elif init == 'ttsvd':
            # Initialize with TT-SVD
            W = dense.weight.detach().t()  # (in_features, out_features) -> (out_features, in_features)
            cores = tt_svd_init_from_dense(W, in_modes, out_modes, ranks)
            with torch.no_grad():
                for i, core in enumerate(cores):
                    mod.cores[i].data.copy_(core)
                if dense.bias is not None and mod.bias is not None:
                    mod.bias.copy_(dense.bias)
        return mod
    else:
        raise ValueError(f"Unsupported module type {type(dense)} for TT conversion")


def apply_recipe_to_model(model: nn.Module, recipe: Recipe) -> Dict:
    """
    Apply a compression recipe to a model.
    
    Args:
        model: Model to compress
        recipe: Compression recipe
    
    Returns:
        Summary dictionary with compression statistics
    """
    summary = {
        'replaced': [],
        'dense_params': count_params(model),
        'errors': []
    }
    
    for tgt in recipe.targets:
        paths = expand_paths(model, tgt.path)
        if not paths:
            summary['errors'].append(f"No modules found for path: {tgt.path}")
            continue
        
        for path in paths:
            try:
                dense = get_module(model, path)
                
                if tgt.decomp.upper() != 'TT':
                    raise NotImplementedError(f'Only TT is supported, got {tgt.decomp}')
                
                # Handle auto-padding/trimming for embeddings
                in_modes = list(tgt.in_modes)
                out_modes = list(tgt.out_modes)
                
                if isinstance(dense, nn.Embedding):
                    # Auto-adjust in_modes for embeddings
                    expected_in = dense.num_embeddings
                    actual_in = 1
                    for m in in_modes:
                        actual_in *= m
                    
                    if actual_in != expected_in:
                        # Adjust by padding or trimming
                        if actual_in < expected_in:
                            # Pad with 1s
                            while actual_in < expected_in:
                                in_modes.append(1)
                                actual_in *= 1
                        else:
                            # Trim (simple: take first modes that fit)
                            adjusted = []
                            prod = 1
                            for m in in_modes:
                                if prod * m <= expected_in:
                                    adjusted.append(m)
                                    prod *= m
                                else:
                                    break
                            # Fill remaining with 1s
                            while prod < expected_in:
                                adjusted.append(1)
                                prod *= 1
                            in_modes = adjusted
                
                tt = make_tt_module_from_dense(dense, in_modes, out_modes, tgt.ranks, init=tgt.init)
                set_module(model, path, tt)
                summary['replaced'].append(path)
            except Exception as e:
                summary['errors'].append(f"Error replacing {path}: {e}")
    
    summary['tt_params'] = count_params(model)
    summary['compression_ratio'] = (
        summary['dense_params'] / summary['tt_params'] 
        if summary['tt_params'] > 0 else 0.0
    )
    
    return summary


def add_penalty_hook(model: nn.Module, recipe: Recipe):
    """
    Add penalty hooks to modules specified in recipe.
    
    Args:
        model: Model to add hooks to
        recipe: Recipe with penalty configurations
    """
    for tgt in recipe.targets:
        if tgt.penalty is None:
            continue
        
        paths = expand_paths(model, tgt.path)
        for path in paths:
            try:
                mod = get_module(model, path)
                attach_penalty_to_module(mod, tgt.penalty)
            except Exception as e:
                # Silently skip if module not found
                pass


def get_compression_stats(model: nn.Module) -> Dict:
    """
    Get compression statistics for a model.
    
    Args:
        model: Model to analyze
    
    Returns:
        Dictionary with compression statistics
    """
    total_params = count_params(model)
    tt_params = 0
    dense_params = 0
    
    for module in model.modules():
        if isinstance(module, (TTLinear, TTEmbedding)):
            tt_params += count_params(module)
        elif isinstance(module, (nn.Linear, nn.Embedding)):
            dense_params += count_params(module)
    
    return {
        'total_params': total_params,
        'tt_params': tt_params,
        'dense_params': dense_params,
        'compression_ratio': dense_params / tt_params if tt_params > 0 else 0.0
    }

