"""Reproduce the compression numbers quoted in the README.

For each TT rank in {full, 32, 16, 8}, every Conv1D in the GPT-2 blocks
(attn.c_attn, attn.c_proj, mlp.c_fc, mlp.c_proj) is replaced by a d=3 TTLinear
initialised by TT-SVD. Reported:

- ratio: dense / TT parameters of the replaced layers (weights + biases);
- logits_rel_err: ||logits_tt - logits_dense||_F / ||logits_dense||_F;
- ppl (pretrained model only): perplexity on the first tokens of WikiText-2 test;
- the same metrics for a truncated SVD of each weight with at most as many
  parameters as its TT replacement (equal-parameter baseline).

Parts:
- tiny: random-init GPT-2 (no download), 3 seeds, mean and std;
- distilgpt2: pretrained weights and WikiText-2 from the Hugging Face Hub.

Usage:
    python -m scripts.reproduce_compression            # both parts
    python -m scripts.reproduce_compression --skip-real  # tiny only, offline
Writes results/compression.json and results/compression.md.
"""
import argparse
import copy
import json
import math
import platform
from pathlib import Path

import torch
import transformers
from transformers import GPT2Config, GPT2LMHeadModel

from src.qtc.apply import apply_recipe_to_model
from src.qtc.recipe import Recipe, Target
from src.qtc.utils import expand_paths, get_module

RANKS = ["full", 32, 16, 8]
LAYERS = ["attn.c_attn", "attn.c_proj", "mlp.c_fc", "mlp.c_proj"]
# d=3 factorisations of the hidden sizes used below
MODES = {64: [4, 4, 4], 192: [4, 8, 6], 256: [4, 8, 8],
         768: [8, 12, 8], 2304: [12, 16, 12], 3072: [16, 16, 12]}
TINY = dict(vocab_size=256, n_positions=64, n_embd=64, n_layer=2, n_head=4)
PPL_TOKENS, PPL_CHUNK = 4096, 512


def full_ranks(in_modes, out_modes):
    a = [m * n for m, n in zip(out_modes, in_modes)]
    return [min(math.prod(a[:k]), math.prod(a[k:])) for k in range(len(a) + 1)]


def layer_paths(model):
    return [p for layer in LAYERS for p in expand_paths(model, f"transformer.h[*].{layer}")]


def tt_recipe(model, rank):
    targets = []
    for layer in LAYERS:
        path = f"transformer.h[*].{layer}"
        w = get_module(model, expand_paths(model, path)[0]).weight  # HF Conv1D: (in, out)
        in_modes, out_modes = MODES[w.shape[0]], MODES[w.shape[1]]
        full = full_ranks(in_modes, out_modes)
        ranks = full if rank == "full" else [min(rank, r) for r in full]
        targets.append(Target(path, "TT", in_modes, out_modes, ranks, init="ttsvd"))
    return Recipe(model="gpt2", targets=targets)


def replaced_params(model):
    return sum(p.numel() for path in layer_paths(model) for p in get_module(model, path).parameters())


def tt_model(model, rank):
    m = copy.deepcopy(model)
    summary = apply_recipe_to_model(m, tt_recipe(m, rank))
    assert not summary["errors"], summary["errors"]
    return m.eval()


def svd_model(model, tt):
    """Best rank-s approximation of each Conv1D weight, s(in+out) <= the TT core count of that layer."""
    m = copy.deepcopy(model)
    params = 0
    for path in layer_paths(model):
        budget = sum(c.numel() for c in get_module(tt, path).cores)
        conv = get_module(m, path)
        n_in, n_out = conv.weight.shape
        s = min(budget // (n_in + n_out), n_in, n_out)
        U, S, Vh = torch.linalg.svd(conv.weight.detach(), full_matrices=False)
        with torch.no_grad():
            conv.weight.copy_((U[:, :s] * S[:s]) @ Vh[:s])
        params += s * (n_in + n_out) + conv.bias.numel()
    return m.eval(), params


@torch.no_grad()
def logits_and_ppl(model, chunks):
    logits, nll, n = [], 0.0, 0
    for ids in chunks:
        out = model(ids, labels=ids)
        logits.append(out.logits)
        nll += out.loss.item() * (ids.numel() - ids.shape[0])
        n += ids.numel() - ids.shape[0]
    return torch.cat(logits), math.exp(nll / n)


def rel(a, b):
    return (torch.linalg.norm(a - b) / torch.linalg.norm(b)).item()


def evaluate(model, chunks):
    dense_params = replaced_params(model)
    ref, ref_ppl = logits_and_ppl(model, chunks)
    rows = []
    for rank in RANKS:
        tt = tt_model(model, rank)
        tt_logits, tt_ppl = logits_and_ppl(tt, chunks)
        tt_params = replaced_params(tt)
        svd, svd_params = svd_model(model, tt)
        svd_logits, svd_ppl = logits_and_ppl(svd, chunks)
        rows.append(dict(rank=rank, dense_params=dense_params,
                         tt_params=tt_params, ratio=dense_params / tt_params,
                         tt_logits_rel_err=rel(tt_logits, ref), tt_ppl=tt_ppl,
                         svd_params=svd_params, svd_ratio=dense_params / svd_params,
                         svd_logits_rel_err=rel(svd_logits, ref), svd_ppl=svd_ppl,
                         dense_ppl=ref_ppl))
        if rank == "full":  # self-check: full TT rank is exact (docs/THEORY.md)
            assert rows[-1]["tt_logits_rel_err"] < 1e-4, rows[-1]
    return rows


def run_tiny(seeds):
    runs = []
    for seed in seeds:
        torch.manual_seed(seed)
        model = GPT2LMHeadModel(GPT2Config(**TINY)).eval()
        chunks = [torch.randint(0, TINY["vocab_size"], (4, TINY["n_positions"]))]
        runs.append(evaluate(model, chunks))
    return runs


def run_real(name):
    from datasets import load_dataset
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(name)
    model = GPT2LMHeadModel.from_pretrained(name).eval()
    text = "\n\n".join(load_dataset("Salesforce/wikitext", "wikitext-2-raw-v1", split="test")["text"])
    ids = tok(text, return_tensors="pt").input_ids[:, :PPL_TOKENS]
    return evaluate(model, list(ids.split(PPL_CHUNK, dim=1)))


def mean_std(xs):
    t = torch.tensor(xs, dtype=torch.float64)
    return t.mean().item(), (t.std().item() if len(xs) > 1 else 0.0)


def markdown(tiny, real, real_name):
    cfg = ", ".join(f"{k}={v}" for k, v in TINY.items())
    lines = [f"**Random-init GPT-2** `GPT2Config({cfg})`, {len(tiny)} seeds, mean ± std of the logits error.", "",
             "| TT rank | TT ratio | TT logits rel. err | SVD ratio (equal params) | SVD logits rel. err |",
             "|---|---|---|---|---|"]
    for i, rank in enumerate(RANKS):
        r = [run[i] for run in tiny]
        tt_m, tt_s = mean_std([x["tt_logits_rel_err"] for x in r])
        sv_m, sv_s = mean_std([x["svd_logits_rel_err"] for x in r])
        ratio, svd_ratio = r[0]["ratio"], r[0]["svd_ratio"]
        lines.append(f"| {rank} | {ratio:.2f}x | {tt_m:.3g} ± {tt_s:.2g} | {svd_ratio:.2f}x | {sv_m:.3g} ± {sv_s:.2g} |")
    if real:
        dense_ppl = real[0]["dense_ppl"]
        lines += ["", f"**{real_name}** (pretrained), perplexity on the first {PPL_TOKENS} tokens of WikiText-2 "
                  f"(raw) test in {PPL_CHUNK}-token chunks. Dense perplexity: {dense_ppl:.2f}.", "",
                  "| TT rank | TT ratio | TT logits rel. err | TT ppl | SVD ratio (equal params) "
                  "| SVD logits rel. err | SVD ppl |",
                  "|---|---|---|---|---|---|---|"]
        for x in real:
            lines.append("| {rank} | {ratio:.2f}x | {tt_logits_rel_err:.3g} | {tt_ppl:.2f} | {svd_ratio:.2f}x "
                         "| {svd_logits_rel_err:.3g} | {svd_ppl:.2f} |".format(**x))
    lines += ["", f"TT on {', '.join(LAYERS)} of every block, d=3, TT-SVD init, no fine-tuning. "
              "Ratio = dense / compressed parameters of those layers (weights + biases)."]
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="distilgpt2")
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--skip-real", action="store_true")
    p.add_argument("--out", default="results")
    args = p.parse_args()

    tiny = run_tiny(args.seeds)
    real = None if args.skip_real else run_real(args.model)

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    env = dict(python=platform.python_version(), torch=torch.__version__,
               transformers=transformers.__version__, platform=platform.platform())
    report = dict(env=env, layers=LAYERS, modes=MODES, tiny_config=TINY, seeds=args.seeds, tiny=tiny,
                  real_model=None if real is None else args.model, real=real)
    (out / "compression.json").write_text(json.dumps(report, indent=2) + "\n")
    md = markdown(tiny, real, args.model)
    (out / "compression.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
