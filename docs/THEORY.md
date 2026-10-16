# Theory: Tensor-Train compression of a weight matrix

This note states the results QCompress relies on, with sources, and says
which ones the test suite checks numerically. Notation follows Oseledets
(2011) and Novikov et al. (2015).

## 1. TT-matrix format

Let $W \in \mathbb{R}^{M \times N}$ with $M = \prod_{k=1}^{d} m_k$ (output
modes, `out_modes`) and $N = \prod_{k=1}^{d} n_k$ (input modes, `in_modes`).
Write a row index as $(i_1,\dots,i_d)$ and a column index as
$(j_1,\dots,j_d)$. The TT-matrix format (Novikov et al., 2015, Section 3.1,
Eq. 3) stores $W$ as

$$
W\big((i_1,\dots,i_d),(j_1,\dots,j_d)\big)
  = G_1[i_1,j_1]\, G_2[i_2,j_2] \cdots G_d[i_d,j_d],
\qquad G_k[i_k,j_k] \in \mathbb{R}^{r_{k-1} \times r_k},
$$

with $r_0 = r_d = 1$. In code, core $k$ is a tensor of shape
$(r_{k-1}, m_k, n_k, r_k)$ (`TTLinear.cores[k]`), and `_contract_cores`
evaluates the product above for all indices at once.

### Parameter count

A $d$-way tensor with mode sizes $a_k$ stored in TT format takes
$\sum_k a_k r_{k-1} r_k$ numbers instead of $\prod_k a_k$ (Novikov et al.,
2015, Section 3). A TT-matrix is the tensor with $a_k = m_k n_k$, so

$$
P_{\mathrm{TT}} = \sum_{k=1}^{d} r_{k-1}\, m_k\, n_k\, r_k
\qquad\text{vs.}\qquad
P_{\mathrm{dense}} = \prod_{k=1}^{d} m_k n_k = MN .
$$

The compression ratio reported by `qtc` is $P_{\mathrm{dense}} / P_{\mathrm{TT}}$
(biases included in `apply_recipe_to_model`, excluded here). The TT count
grows like $d\, r^2 \max_k m_k n_k$ for a maximal rank $r$, so large ratios
need **small** ranks.

## 2. TT-SVD

Group each pair $(i_k, j_k)$ into one index of size $a_k = m_k n_k$, so $W$
becomes a $d$-way tensor $\mathcal{A}$ of shape $(a_1, \dots, a_d)$. Its
$k$-th unfolding is the matrix

$$
A_k \in \mathbb{R}^{(a_1 \cdots a_k) \times (a_{k+1} \cdots a_d)} .
$$

TT-SVD (Oseledets, 2011) sweeps $k = 1,\dots,d-1$: reshape the current
remainder, take a truncated SVD, keep $U$ as core $k$, carry $S V^\top$ to
the next step. `tt_svd_init_from_dense` implements this with **fixed** ranks
(the recipe's `ranks`), not with an accuracy threshold.

### Error bound

Let $\varepsilon_k$ be the error of the best rank-$r_k$ approximation of
$A_k$ (closed form by Section 3):

$$
\varepsilon_k = \min_{\operatorname{rank} B \le r_k} \|A_k - B\|_F
             = \Big(\sum_{i > r_k} \sigma_i(A_k)^2\Big)^{1/2}.
$$

Then the tensor $\mathcal{B}$ returned by TT-SVD with ranks $r_k$ satisfies
(Oseledets, 2011; restated as Theorem 1 in Yu et al., 2023)

$$
\|\mathcal{A} - \mathcal{B}\|_F \le \sqrt{\sum_{k=1}^{d-1} \varepsilon_k^2}.
$$

**Accuracy-driven truncation.** If each step instead keeps the smallest
rank whose discarded part has Frobenius norm at most
$\delta = \dfrac{\varepsilon}{\sqrt{d-1}} \|\mathcal{A}\|_F$, then

$$
\frac{\|\mathcal{A} - \mathcal{B}\|_F}{\|\mathcal{A}\|_F} \le \varepsilon .
$$

This is the original parametrisation of TT-SVD (restated as Algorithm 1 in
Yu et al., 2023). QCompress does not implement this mode; ranks are given
explicitly.

**Quasi-optimality.** Let $\mathcal{A}^{\ast}$ be a best approximation with
TT ranks $\le r_k$. Each unfolding of $\mathcal{A}^{\ast}$ has rank
$\le r_k$, so $\varepsilon_k \le \|\mathcal{A} - \mathcal{A}^{\ast}\|_F$ and

$$
\|\mathcal{A} - \mathcal{B}\|_F \le \sqrt{d-1}\;\|\mathcal{A} - \mathcal{A}^{\ast}\|_F .
$$

**Exactness.** If $r_k \ge \operatorname{rank}(A_k)$ for every $k$, all
$\varepsilon_k = 0$ and TT-SVD is exact.

## 3. Eckart–Young–Mirsky

For a matrix $A$ with singular values $\sigma_1 \ge \sigma_2 \ge \dots$, the
truncated SVD $A_r$ is a best rank-$r$ approximation in the Frobenius norm
(Eckart and Young, 1936) and in every unitarily invariant norm (Mirsky,
1960):

$$
\|A - A_r\|_F = \Big(\sum_{i > r} \sigma_i^2\Big)^{1/2},
\qquad
\|A - A_r\|_2 = \sigma_{r+1}.
$$

This gives the closed form of $\varepsilon_k$, and the natural baseline for
TT: a plain low-rank factorisation $W \approx U V^\top$ with $r(M+N)$
parameters.

## 4. From weight error to output error

For a layer $y = Wx + b$ replaced by $\hat y = \hat W x + b$,

$$
\|y - \hat y\|_2 = \|(W - \hat W)x\|_2
  \le \|W - \hat W\|_2\, \|x\|_2
  \le \|W - \hat W\|_F\, \|x\|_2 .
$$

So the Frobenius bound of Section 2 bounds the error of one layer. It says
nothing direct about the error after several layers and non-linearities;
that has to be measured.

## 5. Why full rank does not compress

Write $P_k = a_1 \cdots a_k$ and $Q_k = a_{k+1} \cdots a_d$, so
$P_0 = Q_d = 1$, $P_d = Q_0 = MN$, and the maximal ("full") TT ranks are
$r_k = \min(P_k, Q_k)$.

**Claim.** If $d \ge 2$, $MN > 1$ and every $r_k$ is full, then
$P_{\mathrm{TT}} > MN$: the compression ratio is below 1.

*Proof.* $P_k$ is non-decreasing and $Q_k$ non-increasing in $k$, and
$P_0 = 1 < MN = Q_0$. Let $k^\ast \ge 1$ be the first index with
$P_{k^\ast} \ge Q_{k^\ast}$; it exists because $Q_d = 1$. Then
$r_{k^\ast-1} = P_{k^\ast-1}$ and $r_{k^\ast} = Q_{k^\ast}$, so core $k^\ast$
alone holds $P_{k^\ast-1}\, a_{k^\ast}\, Q_{k^\ast} = MN$ parameters. There is
at least one other core and it holds at least one parameter. $\square$

For $d = 2$: $P_{\mathrm{TT}} = \min(a_1,a_2)(a_1 + a_2) = MN + \min(a_1,a_2)^2$.

Measured instance (PR #3, random-init `GPT2Config(vocab_size=64,
n_positions=16, n_embd=16, n_layer=1, n_head=2)`, TT on `wte`, `c_attn`,
`c_fc`, `c_proj` at full rank): the logits match to relative error
$4.8 \times 10^{-7}$, but 3968 dense parameters become 7616, a ratio of
$0.52\times$. Compression comes only from truncating ranks, and the price
is the $\varepsilon_k$ of Section 2.

## What the tests check

`tests/test_tt_properties.py` (separate PR) checks: exact reconstruction at
full rank in float64, the Section 2 bound against an independent SVD of each
unfolding, the parameter-count formula, the Section 5 claim, `TTLinear` and
`TTEmbedding` against their dense matrix, and `torch.autograd.gradcheck` on
the cores. Quasi-optimality and the $\varepsilon$-truncation mode are not
tested (the latter is not implemented).

## References

- I. V. Oseledets. *Tensor-Train Decomposition.* SIAM J. Sci. Comput.
  33(5):2295–2317, 2011. doi:[10.1137/090752286](https://doi.org/10.1137/090752286)
- A. Novikov, D. Podoprikhin, A. Osokin, D. Vetrov. *Tensorizing Neural
  Networks.* NIPS 2015. arXiv:[1509.06569](https://arxiv.org/abs/1509.06569)
- C. Eckart, G. Young. *The approximation of one matrix by another of lower
  rank.* Psychometrika 1(3):211–218, 1936.
  doi:[10.1007/BF02288367](https://doi.org/10.1007/BF02288367)
- L. Mirsky. *Symmetric gauge functions and unitarily invariant norms.*
  Q. J. Math. 11(1):50–59, 1960.
  doi:[10.1093/qmath/11.1.50](https://doi.org/10.1093/qmath/11.1.50)
- G. Yu, J. Feng, Z. Chen, X. Cai, L. Qi. *A Randomized Block Krylov Method
  for Tensor Train Approximation.* arXiv:[2308.01480](https://arxiv.org/abs/2308.01480),
  2023. Open-access restatement of TT-SVD (Algorithm 1) and its error bound
  (Theorem 1).

Theorem numbers in Oseledets (2011) are not cited because the publisher
PDF could not be checked; secondary sources disagree on them.
