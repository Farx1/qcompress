**Random-init GPT-2** `GPT2Config(vocab_size=256, n_positions=64, n_embd=64, n_layer=2, n_head=4)`, 3 seeds, mean ± std of the logits error.

| TT rank | TT ratio | TT logits rel. err | SVD ratio (equal params) | SVD logits rel. err |
|---|---|---|---|---|
| full | 0.93x | 9.99e-07 ± 3.1e-08 | 0.93x | 0.182 ± 0.0058 |
| 32 | 0.93x | 9.99e-07 ± 3.1e-08 | 0.93x | 0.182 ± 0.0058 |
| 16 | 1.56x | 0.445 ± 0.0066 | 1.56x | 0.427 ± 0.0078 |
| 8 | 5.47x | 0.555 ± 0.0036 | 5.76x | 0.553 ± 0.0024 |

**distilgpt2** (pretrained), perplexity on the first 4096 tokens of WikiText-2 (raw) test in 512-token chunks. Dense perplexity: 54.55.

| TT rank | TT ratio | TT logits rel. err | TT ppl | SVD ratio (equal params) | SVD logits rel. err | SVD ppl |
|---|---|---|---|---|---|---|
| full | 0.99x | 1.55e-06 | 54.55 | 0.99x | 0.267 | 245.71 |
| 32 | 9.22x | 1.02 | 5291.20 | 9.23x | 0.569 | 6970.42 |
| 16 | 34.81x | 0.801 | 3506.91 | 35.89x | 0.982 | 4086.28 |
| 8 | 119.81x | 0.8 | 3480.67 | 137.69x | 0.778 | 3606.38 |

TT on attn.c_attn, attn.c_proj, mlp.c_fc, mlp.c_proj of every block, d=3, TT-SVD init, no fine-tuning. Ratio = dense / compressed parameters of those layers (weights + biases).
