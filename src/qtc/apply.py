import math
from typing import Dict
import torch
from torch import nn
from .recipe import Recipe, Target
from .utils import expand_paths, get_module, set_module, count_parameters
from transformers.pytorch_utils import Conv1D
from src.tn.tt_layers import TTLinear, TTEmbedding
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
        dense: Dense module (nn.Linear, HF Conv1D or nn.Embedding)
        in_modes: Input mode dimensions
        out_modes: Output mode dimensions
        ranks: TT ranks
        init: 'random', or 'ttsvd' / 'copy' (both: TT-SVD of the dense weight)
    
    Returns:
        TT module (TTLinear or TTEmbedding)
    """
    if isinstance(dense, nn.Embedding):
        expected = (dense.num_embeddings, dense.embedding_dim)
    elif isinstance(dense, nn.Linear):
        expected = (dense.in_features, dense.out_features)
    elif isinstance(dense, Conv1D):
        expected = tuple(dense.weight.shape)  # (in, out)
    else:
        raise ValueError(f"Unsupported module type {type(dense)} for TT conversion")
    got = (math.prod(in_modes), math.prod(out_modes))
    if got != expected:
        raise ValueError(
            f"prod(in_modes), prod(out_modes) = {got} but module needs {expected}; "
            "mode products must match exactly (no auto-padding)"
        )

    if isinstance(dense, nn.Embedding):
        mod = TTEmbedding(in_modes=in_modes, out_modes=out_modes, ranks=ranks)
        if init in ('copy', 'ttsvd'):
            mod.copy_from_dense(dense.weight)
        return mod
    elif isinstance(dense, (nn.Linear, Conv1D)):
        mod = TTLinear(
            in_modes=in_modes, 
            out_modes=out_modes, 
            ranks=ranks, 
            bias=(dense.bias is not None)
        )
        if init in ('copy', 'ttsvd'):
            # HF Conv1D (GPT-2) stores weight as (in, out); nn.Linear as (out, in)
            W = dense.weight.t() if isinstance(dense, Conv1D) else dense.weight
            mod.copy_from_dense(W, dense.bias)
        return mod


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
                
                tt = make_tt_module_from_dense(dense, tgt.in_modes, tgt.out_modes, tgt.ranks, init=tgt.init)
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
        elif isinstance(module, (nn.Linear, Conv1D, nn.Embedding)):
            dense_params += count_params(module)
    
    return {
        'total_params': total_params,
        'tt_params': tt_params,
        'dense_params': dense_params,
        'compression_ratio': dense_params / tt_params if tt_params > 0 else 0.0
    }

