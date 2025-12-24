from typing import Dict, Optional
import torch
from torch import nn
from .math_utils import unfolding_singular_values, renyi_entropy, shannon_entropy, nuclear_norm


def attach_penalty_to_module(module: nn.Module, cfg: Dict):
    """
    Attach an extra loss term during training to push TT ranks down indirectly.
    
    Args:
        module: Module to attach penalty to (must have reconstruct_weight method)
        cfg: Penalty configuration dict with keys:
            - type: 'renyi', 'shannon', or 'nuclear'
            - alpha: Rényi parameter (if type='renyi')
            - lambda: Penalty weight
    """
    if not hasattr(module, 'reconstruct_weight'):
        return
    
    penalty_type = cfg.get('type', 'renyi').lower()
    alpha = float(cfg.get('alpha', 2.0))
    lmbd = float(cfg.get('lambda', 1e-4))

    def penalty_hook(module, inputs, output):
        """Hook that computes penalty during forward pass"""
        if not module.training:
            return
        
        try:
            W = module.reconstruct_weight().detach()
            if W is None:
                return
            
            # Compute singular values across a few unfoldings
            svs = unfolding_singular_values(W, module)
            loss = 0.0
            
            for s in svs:
                p = s / (s.sum() + 1e-12)
                
                if penalty_type == 'renyi':
                    ent = renyi_entropy(s, alpha=alpha)
                elif penalty_type == 'shannon':
                    ent = shannon_entropy(s)
                else:
                    # nuclear surrogate
                    ent = s.sum()
                
                loss = loss + ent
            
            module._extra_loss = lmbd * loss
        except Exception as e:
            # Silently fail if penalty computation fails
            module._extra_loss = 0.0

    module.register_forward_hook(penalty_hook)


class PenaltyCollector(nn.Module):
    """
    Wrapper module that collects penalty losses from all modules and adds them to the main loss.
    """
    
    def __init__(self, model: nn.Module):
        super().__init__()
        self.model = model
    
    def forward(self, *args, **kwargs):
        """Forward pass that collects and adds penalty losses"""
        out = self.model(*args, **kwargs)
        extra = 0.0
        
        # Collect penalties from all modules
        for m in self.model.modules():
            if hasattr(m, '_extra_loss'):
                extra = extra + m._extra_loss
                m._extra_loss = 0.0
        
        # Add to loss if available
        if isinstance(out, dict) and 'loss' in out and isinstance(out['loss'], torch.Tensor):
            out['loss'] = out['loss'] + extra
        elif hasattr(out, 'loss') and out.loss is not None:
            out.loss = out.loss + extra
        
        return out


def compute_penalty_metrics(model: nn.Module) -> Dict[str, float]:
    """
    Compute penalty metrics for all modules in a model.
    
    Args:
        model: Model to compute metrics for
    
    Returns:
        Dictionary of penalty metrics
    """
    metrics = {}
    total_penalty = 0.0
    num_modules = 0
    
    for name, module in model.named_modules():
        if hasattr(module, '_extra_loss'):
            penalty = module._extra_loss.item() if isinstance(module._extra_loss, torch.Tensor) else 0.0
            metrics[f'{name}_penalty'] = penalty
            total_penalty += penalty
            num_modules += 1
    
    metrics['total_penalty'] = total_penalty
    metrics['num_penalty_modules'] = num_modules
    
    return metrics


def get_penalty_config(penalty_type: str = 'renyi', alpha: float = 2.0, lambda_val: float = 1e-4) -> Dict:
    """
    Get a standard penalty configuration.
    
    Args:
        penalty_type: Type of penalty ('renyi', 'shannon', 'nuclear')
        alpha: Rényi parameter
        lambda_val: Penalty weight
    
    Returns:
        Penalty configuration dict
    """
    return {
        'type': penalty_type,
        'alpha': alpha,
        'lambda': lambda_val
    }

