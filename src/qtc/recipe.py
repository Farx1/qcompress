import yaml
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Target:
    """Target module configuration for compression"""
    path: str
    decomp: str  # 'TT' (MPO later)
    in_modes: List[int]
    out_modes: List[int]
    ranks: List[int]
    init: str = 'random'  # 'random' | 'ttsvd' | 'copy'
    penalty: Optional[Dict] = None


@dataclass
class Recipe:
    """Compression recipe configuration"""
    model: str
    seed: int = 42
    budget: str = ''
    targets: List[Target] = field(default_factory=list)


def load_recipe(path: str) -> Recipe:
    """
    Load a compression recipe from a YAML file.
    
    Args:
        path: Path to YAML recipe file
    
    Returns:
        Recipe object
    """
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    targets = []
    for t in data.get('targets', []):
        target = Target(
            path=t.get('path', ''),
            decomp=t.get('decomp', 'TT'),
            in_modes=t.get('in_modes', []),
            out_modes=t.get('out_modes', []),
            ranks=t.get('ranks', []),
            init=t.get('init', 'random'),
            penalty=t.get('penalty')
        )
        targets.append(target)
    
    return Recipe(
        model=data.get('model', ''),
        seed=data.get('seed', 42),
        budget=data.get('budget', ''),
        targets=targets
    )


def save_recipe(recipe: Recipe, path: str):
    """
    Save a compression recipe to a YAML file.
    
    Args:
        recipe: Recipe object to save
        path: Path to save YAML file
    """
    data = {
        'model': recipe.model,
        'seed': recipe.seed,
        'budget': recipe.budget,
        'targets': []
    }
    
    for target in recipe.targets:
        target_dict = {
            'path': target.path,
            'decomp': target.decomp,
            'in_modes': target.in_modes,
            'out_modes': target.out_modes,
            'ranks': target.ranks,
            'init': target.init
        }
        if target.penalty is not None:
            target_dict['penalty'] = target.penalty
        data['targets'].append(target_dict)
    
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

