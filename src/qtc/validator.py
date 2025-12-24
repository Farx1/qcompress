from typing import List, Dict, Optional, Tuple
import torch
from torch import nn
from .recipe import Recipe, Target
from .utils import get_module, expand_paths


class RecipeValidator:
    """Validator for compression recipes"""
    
    def __init__(self, model: nn.Module):
        self.model = model
        self.errors = []
        self.warnings = []
    
    def validate(self, recipe: Recipe) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a recipe against the model.
        
        Args:
            recipe: Recipe to validate
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Validate each target
        for i, target in enumerate(recipe.targets):
            self._validate_target(target, i)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_target(self, target: Target, index: int):
        """Validate a single target"""
        # Check path exists
        paths = expand_paths(self.model, target.path)
        if not paths:
            self.errors.append(
                f"Target {index}: Path '{target.path}' does not match any modules"
            )
            return
        
        # Validate each expanded path
        for path in paths:
            try:
                module = get_module(self.model, path)
                self._validate_module(module, target, path)
            except (AttributeError, KeyError, IndexError) as e:
                self.errors.append(
                    f"Target {index}: Cannot access module at path '{path}': {e}"
                )
    
    def _validate_module(self, module: nn.Module, target: Target, path: str):
        """Validate a module against target configuration"""
        # Check module type
        if not isinstance(module, (nn.Linear, nn.Embedding)):
            self.warnings.append(
                f"Path '{path}': Module type {type(module)} may not be supported"
            )
            return
        
        # Validate dimensions
        if isinstance(module, nn.Linear):
            expected_in = module.in_features
            expected_out = module.out_features
        else:  # nn.Embedding
            expected_in = module.num_embeddings
            expected_out = module.embedding_dim
        
        # Check mode products
        in_product = 1
        for m in target.in_modes:
            in_product *= m
        
        out_product = 1
        for m in target.out_modes:
            out_product *= m
        
        # Allow some flexibility for embeddings (auto-padding/trimming)
        if isinstance(module, nn.Embedding):
            if abs(in_product - expected_in) > expected_in * 0.1:  # 10% tolerance
                self.warnings.append(
                    f"Path '{path}': in_modes product {in_product} != num_embeddings {expected_in} "
                    f"(will be auto-adjusted)"
                )
        else:
            if in_product != expected_in:
                self.errors.append(
                    f"Path '{path}': in_modes product {in_product} != in_features {expected_in}"
                )
        
        if out_product != expected_out:
            self.errors.append(
                f"Path '{path}': out_modes product {out_product} != out_features {expected_out}"
            )
        
        # Validate ranks
        expected_ranks_len = len(target.in_modes) + 1
        if len(target.ranks) != expected_ranks_len:
            self.errors.append(
                f"Path '{path}': ranks length {len(target.ranks)} != expected {expected_ranks_len}"
            )
        
        if target.ranks and (target.ranks[0] != 1 or target.ranks[-1] != 1):
            self.errors.append(
                f"Path '{path}': ranks must start and end with 1, got {target.ranks[0]} and {target.ranks[-1]}"
            )
        
        # Validate decomp type
        if target.decomp.upper() != 'TT':
            self.errors.append(
                f"Path '{path}': Only 'TT' decomposition is supported, got '{target.decomp}'"
            )
        
        # Validate init type
        if target.init not in ['random', 'ttsvd', 'copy']:
            self.warnings.append(
                f"Path '{path}': Unknown init type '{target.init}', using 'random'"
            )


def validate_recipe(model: nn.Module, recipe: Recipe) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate a recipe.
    
    Args:
        model: Model to validate against
        recipe: Recipe to validate
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = RecipeValidator(model)
    return validator.validate(recipe)

