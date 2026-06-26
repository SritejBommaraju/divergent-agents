# Benchmark results — honest edition

*Design and metrics were pre-registered in [`BENCHMARKING.md`](BENCHMARKING.md) before scoring. Raw
generations and scores are committed in [`bench/data/`](bench/data/); re-run with `python bench/run_dat.py`.
The point of this page is to report what we found, **including where the engine does not help.***

## TL;DR

> **Prompting an LLM to "be divergent" did not measurably increase divergence. The engine's
> *structural* memory (a cross-response novelty archive) did — by a large, highly significant margin —
> and at no cost to per-response quality.** That is the thesis of this whole repo, measured: divergence
> is a property of the *loop*, not the *forward pass*.

## Setup (DAT, the no-judge objective spine)

Divergent Association Task: produce 10 maximally-unrelated nouns; score = mean pairwise cosine distance
of the first 7, averaged over a **3-model embedding ensemble** (no LLM in the scoring loop). Three
conditions, same model (claude-opus-4-8), one generation per trial:

- **baseline** — the standard validated DAT instruction (a *strong* baseline: it already asks for difference). N=30.
- **divergence** — baseline + the engine's Stage-1 prompt (verbalized sampling + forced distant-domain lenses). N=30.
- **archive** — the engine's Stage-2 mechanism: sequential generation where each response must avoid
  every word used before (a growing novelty archive, 200 words by the end). N=20.

Reporting **both** axes the literature demands (per-response *and* population), with 95% bootstrap CIs
and 20k-iteration permutation tests vs baseline.

## Results

| Axis (what it measures) | baseline | divergence | archive | archive vs baseline |
|---|---|---|---|---|
| **1. Within-response DAT** — is each answer internally spread? | 99.71 `[99.2,100.2]` | 99.63 `[99.1,100.2]` | 99.42 `[98.8,100.0]` | Δ −0.28, **p=0.50 (n.s.)** |
| **2. Population spread** — are independent answers distinct? | 0.625 `[0.60,0.65]` | 0.649 `[0.63,0.67]` | **0.853 `[0.85,0.86]`** | Δ +0.229, **p<0.0001** |
| **3. Lexical overlap** — recurring-word reuse (lower better) | 0.154 | 0.134 | **0.000** | Δ −0.154, **p<0.0001** |
| Type/token ratio (model-free) | 0.337 | 0.330 | **1.000** | — |
| Attractor vocabulary | `volcano×26, whisper×20, umbrella×14` | `lullaby×20, grief×19, barnacle×18` | none (all unique) | — |

Population spread (AXIS 2), bar = value on 0–1:

```
baseline    |█████████████████████████·············| 0.625
divergence  |██████████████████████████············| 0.649   (Δ vs base p=0.14, n.s.)
archive     |██████████████████████████████████····| 0.853   (Δ vs base p<0.0001, ***)
```

## What this shows (read carefully — the nuance is the point)

1. **Prompting alone is a null result.** The Stage-1 "be divergent" prompt does **not** significantly
   beat the standard DAT instruction on *any* axis (within-response p=0.84; population p=0.14). It
   merely **relocates the attractor** — the model stops saying *volcano/whisper* and starts saying
   *grief/lullaby/barnacle* — while the *amount* of collapse (type/token 0.33) is unchanged. This is
   precisely the population-homogeneity effect of [Wenger & Kenett 2025](https://arxiv.org/abs/2501.19361),
   reproduced here in our own pipeline. **We will not pretend the prompt worked. It didn't.**

2. **Structure works, and significantly.** The Stage-2 archive lifts population diversity by **+0.229
   (p<0.0001)** and drives lexical overlap to zero — the exact axis prompting could not move.

3. **The non-trivial part — it's not free word-banning.** Forcing non-repetition *trivially* zeroes
   AXIS 3. The honest question is whether that **wrecks per-response quality** — does the model, starved
   of its favourite words, start emitting worse lists? **It does not:** AXIS 1 within-response DAT is
   statistically unchanged (99.42 vs 99.71, p=0.50) even with a 200-word ban-list. So the archive buys
   a large population-diversity gain **at no measurable cost to per-response divergence.** That is the
   real finding.

**Mechanistic reading:** a single forward pass — even one explicitly told to diverge — samples from a
collapsed distribution. The thing that escapes the collapse is *memory across responses*: the loop
remembering what it already said and refusing to repeat it. Intelligence in the loop, not the pass.

## Honest caveats and limitations

- **AXIS 1 has a ceiling.** Baseline DAT is already ~99.7 (the clustered-words control scores ~82–94),
  so there is little headroom for *any* method to raise per-response divergence on DAT. We therefore
  **cannot** claim the engine improves per-response divergence — only that it doesn't sacrifice it.
- **Part of the archive's win is by construction.** AXIS 3 → 0 is mechanical (you banned the words).
  The load-bearing, non-mechanical result is AXIS 2 ↑ *with* AXIS 1 flat. We say so plainly.
- **Vocabulary exhaustion is a real limit.** The archive held quality to 200 banned words; it must
  eventually degrade as the model runs out of good nouns. A semantic (not exact-match) archive — the
  embedding-distance ban the real engine uses — would push that limit further, but it is not infinite.
- **DAT is a narrow proxy.** It validates the Stage-2 *mechanism* cleanly; it does **not** prove the
  full engine writes better novel *code*. That needs the pass@k / ideation benchmarks below.
- **Single model family.** All generation and the (avoided) judging would be Claude; per
  [`BENCHMARKING.md`](BENCHMARKING.md) P4 we deliberately made **no** LLM-judge claims to avoid grading
  our own homework. The embedding scorer is an ML artifact too (a proxy with a ceiling), which is why
  we ensemble it and report CIs.
- **Compute.** Conditions are matched at one generation per trial; the archive uses more *input* tokens
  (the ban-list) but the same number of generations. The full fan-out engine is far more expensive
  (~0.7M tokens for one design task) — its value must be judged compute-matched (P5), which the DAT
  spine does not test.

## What we have NOT yet done (and why it's the honest next step)

Per [`BENCHMARKING.md`](BENCHMARKING.md) P5, the decisive test for *useful* outside-the-box problem-solving
is a **compute-matched pass@k coverage** benchmark on verifiable coding tasks: does the engine's diverse
candidates cover more *distinct correct* solutions than equal-budget best-of-N, out to large k, beating
a dumb-guessing control? That requires a sandboxed test oracle and a real token budget; it is scoped and
specified but not yet run at scale. A blind, length-controlled ideation comparison is the other next step
— gated on access to a cross-family judge so it stays honest. We flag these rather than over-claim from
the DAT proxy.

## Reproduce

```bash
python bench/score.py            # scorer self-check
python bench/run_dat.py          # the table above, from bench/data/dat_raw.json
python bench/recheck_methodology.py   # re-verify the methodology citations
```
