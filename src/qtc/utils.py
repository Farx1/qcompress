from typing import Any, List
import re


def expand_paths(model, pattern: str) -> List[str]:
    """
    Resolve module paths with wildcards like transformer.h[*].mlp.c_fc
    
    Args:
        model: PyTorch model
        pattern: Path pattern with optional [*] wildcard
    
    Returns:
        List of resolved paths
    """
    if '[*]' not in pattern:
        return [pattern]
    
    prefix, suffix = pattern.split('[*]', 1)
    # Remove trailing dot if present
    prefix = prefix.rstrip('.')
    
    # Get the module at prefix
    try:
        node = get_module(model, prefix)
    except (AttributeError, KeyError, IndexError):
        return []
    
    # Check if it's a list/sequential module
    if not hasattr(node, '__len__') or not hasattr(node, '__getitem__'):
        return []
    
    # Expand wildcard
    out = []
    for i in range(len(node)):
        if suffix.startswith('.'):
            expanded = f"{prefix}.{i}{suffix}"
        else:
            expanded = f"{prefix}.{i}.{suffix}"
        out.append(expanded)
    
    return out


def get_module(root, path: str):
    """
    Get a module from a model by path string.
    
    Args:
        root: Root module
        path: Dot-separated path (e.g., 'transformer.h.0.mlp.c_fc')
    
    Returns:
        Module at path
    """
    cur = root
    for name in path.split('.'):
        if not name:
            continue
        if name.isdigit():
            cur = cur[int(name)]
        else:
            cur = getattr(cur, name)
    return cur


def set_module(root, path: str, new):
    """
    Set a module in a model by path string.
    
    Args:
        root: Root module
        path: Dot-separated path
        new: New module to set
    """
    parts = path.split('.')
    parent_path = '.'.join(parts[:-1])
    leaf = parts[-1]
    
    if parent_path:
        parent = get_module(root, parent_path)
    else:
        parent = root
    
    setattr(parent, leaf, new)


def count_parameters(model) -> int:
    """
    Count total number of parameters in a model.
    
    Args:
        model: PyTorch model
    
    Returns:
        Total parameter count
    """
    return sum(p.numel() for p in model.parameters())


def format_number(n: int) -> str:
    """
    Format a number with K/M/B suffixes.
    
    Args:
        n: Number to format
    
    Returns:
        Formatted string
    """
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.2f}K"
    else:
        return str(n)

