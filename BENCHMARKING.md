# How to benchmark "thinking outside the box" — honestly

*The hardest part of this project is not building a divergence engine — it's proving it works without
fooling ourselves. Creativity benchmarks are unusually easy to rig: the metric you reach for first
(lexical difference, an LLM judge, raw coverage) tends to reward exactly the artifacts that look like
divergence without being it. This document is the honest tactic, derived from 23 verified papers
([appendix](bench/methodology_papers.md), all re-checked — see `bench/recheck_methodology.py`).*

## The five principles

### P1 — Make the spine a *no-judge*, objective metric
The cleanest divergence measure has **no grader in the loop**: the **Divergent Association Task**
(name 10 maximally-unrelated nouns; score = mean pairwise embedding distance of 7 of them) correlates
with human creativity as well as classic tasks correlate with each other, and is fully automatic
([Olson et al., PNAS 2021](https://www.pnas.org/doi/10.1073/pnas.2022340118)). A function can't grade
its own homework, so this is the honest backbone.
- **Don't cherry-pick the embedding space.** Average over a fixed *ensemble* of public models; one
  model's quirks wash out ([SemDis, Beaty & Johnson 2021](https://doi.org/10.3758/s13428-020-01453-w)).
  We use three (`potion-base-8M`, `potion-base-32M`, `potion-retrieval-32M`).
- **Control length.** Semantic-distance originality is confounded by elaboration and fluency — longer
  answers score higher mechanically ([Beaty et al. 2022](https://doi.org/10.1080/10400419.2022.2025720)).
  DAT fixes this *by construction* (fixed word count), which is exactly why it's the spine.

### P2 — Separate *per-response* novelty from *population* diversity
The single most important honesty correction: an LLM can score as original as a human on each *single*
response while the *population* of its responses collapses onto the same few outputs
([Wenger & Kenett 2025, "We're Different, We're the Same", arXiv:2501.19361](https://arxiv.org/abs/2501.19361);
[NoveltyBench, arXiv:2504.05228](https://arxiv.org/abs/2504.05228)). A per-item mean **hides** mode
collapse. So every result reports **both** axes: within-response spread *and* between-response spread
(plus a model-free lexical-overlap cross-check). Our own DAT run shows why this matters — see
[`RESULTS.md`](RESULTS.md).

### P3 — Novelty without quality is noise
A judge (or a metric) can be steered to reward weird, wrong, or incoherent output as "creative." Score
originality **jointly** with validity/usefulness as separate dimensions, and for problem-solving demand
a real correctness oracle ([LiveIdeaBench, arXiv:2412.17596](https://arxiv.org/abs/2412.17596);
[Measuring LLM Novelty, arXiv:2504.09389](https://arxiv.org/abs/2504.09389)). "More novel" only counts
among outputs that clear the quality bar — which is also how the engine's Stage 6 selects.

### P4 — If you use an LLM judge, assume it lies in your favor
LLM judges systematically over-rate **longer** answers, **their own style**, and **familiar
(low-perplexity)** text, and flip verdicts on answer **order**
([Self-Preference Bias, arXiv:2410.21819](https://arxiv.org/abs/2410.21819);
[LLMs are not fair evaluators, arXiv:2305.17926](https://arxiv.org/abs/2305.17926);
[MT-Bench, arXiv:2306.05685](https://arxiv.org/abs/2306.05685);
[length-controlled AlpacaEval, arXiv:2404.04475](https://arxiv.org/abs/2404.04475);
[Judging the Judges, arXiv:2406.07791](https://arxiv.org/abs/2406.07791)).
If a judge is unavoidable: **blind** it, **counterbalance order** and report flip-rate, **length-control**,
use a judge from a **different model family** than the system under test, and **validate against human
labels** ([G-Eval caveats, arXiv:2303.16634](https://arxiv.org/abs/2303.16634)).
> **Our honest limitation:** the only models available here are Claude variants, so we cannot run a
> clean cross-family judge. Therefore we **refuse to make any headline claim from an LLM judge** and
> lean entirely on the no-judge objective metrics (P1–P2). Grading our own homework is the one thing
> we will not do.

### P5 — For problem-solving: compute-match, and never confuse coverage with accuracy
A multi-sample engine vs one greedy decode is a rigged fight. The honest protocol:
- **Charge the engine for all of its compute** (rollouts + search + verifier) and give the baseline an
  equal-budget best-of-N ([Snell et al., arXiv:2408.03314](https://arxiv.org/abs/2408.03314)).
- Use the **unbiased pass@k estimator** with n≫k and bootstrap CIs
  ([Chen et al., arXiv:2107.03374](https://arxiv.org/abs/2107.03374)).
- **Coverage ≠ accuracy.** pass@k (does the answer ever appear) only becomes useful with a verifier to
  pick it; verifier-free selection plateaus while coverage climbs
  ([Large Language Monkeys, arXiv:2407.21787](https://arxiv.org/abs/2407.21787)).
- **Report the full pass@k curve to large k.** A method can win at pass@1 yet the base model overtakes
  at large k — meaning it only re-weighted reachable solutions, not expanded the frontier
  ([Yue et al., arXiv:2504.13837](https://arxiv.org/abs/2504.13837)).
- **Add a dumb-guessing control** (enumerate the most frequent answers); coverage gains must beat it
  ([Yona et al., arXiv:2410.15466](https://arxiv.org/abs/2410.15466)).

## The tactic we adopt (and its honest scope)

1. **DAT objective spine** — the headline test. Standard DAT instruction (a *strong* baseline that
   already asks for difference) vs the engine's divergence mechanisms, scored with the ensemble on all
   three axes of P2, with bootstrap CIs and permutation tests. *Pre-registered* metrics below.
2. **Archive ablation** — isolate the engine's Stage-2 mechanism (cross-response novelty archive) to
   test whether *structure*, not prompting, is what moves the population axis.
3. **Recommended next stage** (scoped, not yet run at scale): a compute-matched pass@k coverage test on
   verifiable coding tasks (P5) and a blind, length-controlled ideation comparison — both flagged with
   the cost and the cross-family-judge caveat so the claims stay honest.

### Pre-registration (write the ruler before reading the tape)
- **Metric:** mean pairwise cosine distance over a 3-model embedding ensemble; DAT uses the first 7
  valid single-word nouns ×100; population spread = mean inter-trial centroid distance; lexical overlap
  = mean inter-trial Jaccard.
- **Conditions:** `baseline` (standard DAT), `divergence` (Stage-1 prompt), `archive` (Stage-2,
  sequential ban-list). **N=30** per parallel condition, **N=20** sequential.
- **Stats:** 10k-sample bootstrap 95% CI; 20k-iteration permutation test; significance at p<0.05.
- **Seeds fixed; raw generations and scores committed** (`bench/data/`) so every number is reproducible.

The results — including where the engine **fails** to beat baseline — are in [`RESULTS.md`](RESULTS.md).
