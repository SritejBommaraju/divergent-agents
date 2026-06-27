# Benchmark results — honest edition

*Design and metrics were pre-registered in [`BENCHMARKING.md`](BENCHMARKING.md) before scoring. Raw
generations and scores are committed in [`bench/data/`](bench/data/); re-run with `python bench/run_dat.py`.
The point of this page is to report what we found, **including where the engine does not help.***

## TL;DR

> **Three honest findings that triangulate the thesis:**
> 1. On word-generation (DAT), prompting an LLM to "be divergent" did **not** measurably increase
>    divergence — it just relocates the cliché vocabulary. *(Benchmark 1)*
> 2. The engine's *structural* memory (a cross-response novelty archive) **did** — a large, highly
>    significant gain in population diversity at no cost to per-response quality. *(Benchmark 1)*
> 3. On code, best-of-N collapses to essentially **one** algorithm (mode collapse, quantified); the
>    engine's forced-lens mechanism produces ~9× more distinct correct solutions. *(Benchmark 2)*
> 4. Properly measured, there is **no pass@k accuracy headroom** for the engine at this model's strength
>    — a frontier model is at the ceiling on anything construct-and-check *(Benchmark 4)* — BUT under
>    adversarial fuzzing, diversity becomes a **correctness oracle**: differential testing over diverse
>    solutions catches subtle bugs a single pass ships, recovering the right answer 383/383 times. *(Benchmark 5)*
>
> The through-line: a single forward pass collapses onto the mode *and* is confidently alone; escaping
> both requires *structure* — memory across responses, access to a strategy space, and diverse solutions
> that cross-check each other. Divergence lives in the **loop**, not the forward pass.

## Benchmark 1 — DAT (the no-judge objective spine)

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

## Benchmark 2 — coding solution diversity (best-of-N vs lens-diverse engine)

Does divergence prompting actually diversify *code*? Three problems with many valid algorithms (`fib`,
`is_palindrome`, `primes_up_to`), each generated 10× by **baseline** (identical prompt, i.e. best-of-N)
and by the **engine** (10 distinct approach-lenses) — compute-matched at 10 generations. Every candidate
is executed against a trusted checker in an isolated subprocess; among the *correct* ones we count
**structurally distinct algorithms** (AST-skeleton clusters, identifiers erased) and semantic spread.

| problem | distinct algorithms /10 | top-cluster share | semantic spread | correct |
|---|---|---|---|---|
| fib — baseline | 1 | 1.00 | 0.00 | 10/10 |
| fib — **engine** | **9** | **0.20** | **0.51** | 10/10 |
| palindrome — baseline | 1 | 1.00 | 0.17 | 10/10 |
| palindrome — **engine** | **10** | **0.10** | **0.44** | 10/10 |
| primes — baseline | 2 | 0.90 | 0.01 | 10/10 |
| primes — **engine** | **9** | **0.20** | **0.31** | 10/10 |
| **aggregate** | base **1.33** → eng **9.33** | base **0.97** → eng **0.17** | base **0.06** → eng **0.42** | 30/30 both |

**What this shows.** Best-of-N exhibits **severe mode collapse on real code**: all 10 baseline `fib`
samples were *byte-for-byte identical*, and across problems best-of-N produced a mean of **1.33** distinct
algorithms with **97%** of samples in a single cluster. The engine's forced-lens mechanism produced
**9.33** distinct correct algorithms (fast-doubling, recursion, memoization, functional `reduce`,
generators, lookup tables…) — **7× more solution-space coverage, with correctness fully preserved (30/30).**

**The honest contrast with Benchmark 1 is the real insight.** Divergence prompting *failed* to diversify
*words* (DAT) but *succeeded* dramatically at diversifying *code*. Why? Code has a rich space of
*nameable* strategies the model already knows (recursive/iterative/closed-form/…), which explicit lenses
can unlock; "unrelated nouns" has no such strategy space, only a vocabulary attractor. **Divergence
prompting works when, and only when, the task has structured alternatives the model can be pointed at.**

**Honest caveats.**
- The engine condition received *explicit* approach instructions, so the diversity was partly **requested,
  not emergent**. The fair claim is two-fold and we state both: (a) best-of-N has near-zero algorithmic
  diversity — mode collapse on code is real and severe; (b) the engine's lens mechanism reliably escapes
  it. We do **not** claim the model spontaneously diversifies.
- Correctness is **saturated** (these problems are easy), so this measures *diversity*, **not** whether
  any diverse solution is *better*. All were correct; none was superior. The demonstrated value is
  escaping the monoculture, not finding a winning solution — that is what Benchmark 3 (below) would test.
- n=3 problems: descriptive, a complement to the inferential DAT result, reported as such.

## Benchmark 3 — cognitive routing (does matching the mode to the problem help?)

v2 added a **metacognitive router** + a 12-mode library (see [`COGNITION.md`](COGNITION.md)). Two
questions: does picking the right *mode* raise accuracy, and does the router actually *differentiate*?

**Accuracy: an honest ceiling-bound null.** On 15 reasoning tasks across two difficulty tiers (logic,
Bayesian, combinatorics, induction, arithmetic, code), each solved by **baseline**, **always-divergent**,
and **router** strategies (3–5 samples each), every strategy scored **100%**:

| | baseline | always-divergent | router |
|---|---|---|---|
| easy set (8 tasks, n=3) | 1.00 | 1.00 | 1.00 |
| hard set (7 novel tasks, n=5) | 1.00 | 1.00 | 1.00 |

A frontier model already solves any task we can *construct and check*, so the thinking *strategy* can't
move *accuracy*. We report this as a null, not a win. **Methodology note (kept as a lesson):** our first
hard-set score falsely showed "scaffolding hurts" — a **grading artifact** where verbose router/divergent
answers were marked wrong for *mentioning* distractor names ("Quinn… if **Pat**…"). Fixing the scorer to
grade the *stated* answer erased the effect. The checker is part of the experiment.

**Differentiation: a clear win** ([`demos/02-router-differentiation.md`](demos/02-router-differentiation.md)).
Given 10 varied tasks, the router produced **9 distinct mode-plans / 8 distinct primary modes** — it did
**not** collapse to "always brainstorm." Diagnosis → `abductive→causal→verify`; proof → `deductive→verify`;
Fermi estimate → `decompose→bayesian→verify`; trade-off → `first_principles→dialectic→verify`; and it
reaches for `divergent` *only* on the two genuinely open tasks.

**Honest synthesis of v2.** The value of "more kinds of thinking" is **not** higher accuracy on solvable
problems (null) — it is *breadth + adaptivity* (the router deploys the right mode, demonstrated) and
*solution-space coverage* on open problems (Benchmark 2's 9× distinct correct solutions), with **no
accuracy regression**. We have **not** shown routing beats a strong model thinking hard on problems it
can't already solve; that needs beyond-ceiling tasks (below).

## Benchmark 4 — proper pass@k on NOVEL problems (the decisive test, done right)

To finally chase headroom, I built **novel twists** on known algorithms — 3-way interleaving, diagonal
path-counting, exactly-k word-break, non-adjacent subsequences, two-bracket validity, strictly-increasing
paths — so memorized templates are *wrong*. Each has a **brute-force reference cross-validated against an
independent enumeration on 350+ cases** ([`bench/code_twist.py`](bench/code_twist.py)), so the checker is
unimpeachable. Scored per [`BENCHMARKING.md`](BENCHMARKING.md) P5: compute-matched best-of-N vs engine-diverse,
**unbiased pass@k estimator**, **non-oracle selected-accuracy** (majority vote on *public* examples only —
no hidden-test leakage), coverage, bootstrap CIs (6 problems, n=6/cell).

| metric | baseline best-of-N | engine (diverse) |
|---|---|---|
| pass@1 | 0.972 `[0.92,1.00]` | 1.000 `[1.00,1.00]` |
| pass@2 … pass@6 | 1.000 | 1.000 |
| selected-accuracy (non-oracle) | 1.000 | 1.000 |
| coverage | 1.000 | 1.000 |

**Honest reading.** Even on novel problems built to defeat memorization, opus-4.8 at low effort sits at a
near-perfect pass@1 ceiling. The engine's diversity closed the single pass@1 miss (one `gap` sample), but
plain best-of-N also reaches 1.0 by k=2 — so **at matched compute there is no significant coverage
advantage.** This is precisely the negative result the literature predicts when pass@1 saturates
([Yue et al. 2504.13837](https://arxiv.org/abs/2504.13837)): with no coverage gap, a multi-sample engine
has nothing to add. Across **four** benchmark families now (DAT, easy + hard reasoning, novel coding) the
finding is robust: *a frontier model has no construct-and-check headroom at low effort.* We report it
straight rather than manufacture a win.

## Benchmark 5 — robustness under fuzzing: diversity as a correctness oracle

Benchmark 4 used ~26 *fixed* inputs per problem. A small test set can hide rare bugs, so we re-evaluated
every generated solution against **2000 random adversarial inputs** per problem, checked against the
trusted brute reference ([`bench/fuzz_eval.py`](bench/fuzz_eval.py)). This is the first benchmark to show
the engine winning on **correctness**.

- **The fixed-test ceiling was slightly optimistic.** 2 of 72 solutions (one `gap`, one `bracket`)
  **passed the fixed tests but FAIL under fuzzing** — subtle bugs the weak set never triggered. (Fuzzed
  pass@1 is still 0.972, so this is robustness, *not* a pass@k coverage gap — the ceiling on coverage holds.)
- **Differential testing turns diversity into a free correctness oracle.** Flagging inputs where the
  diverse solutions *disagree* exposed **383 bug-revealing inputs with no reference at all**; **majority
  vote was correct on 383 / 383 = 100%** of them. A single forward pass ships a buggy solution on ~0.33%
  of inputs (≈1 in 36 solutions harbors such a bug); the engine's diverse-generate → differential-test →
  majority-vote catches and corrects it.
- **Concrete:** `num_gap_subseq("abaaa","aa")` → 11 solutions say **4** (correct), 1 says 2; the buggy
  minority is outvoted. Full demo + the reusable mechanism: [`demos/04-differential-testing.md`](demos/04-differential-testing.md),
  [`engine/diff_test.py`](engine/diff_test.py) (self-checked on a planted bug).

**Honest limit (stated in the tool itself):** this catches *idiosyncratic* (minority) bugs. A
**systematic** bug shared by the majority survives — disagreement is a strong "investigate" signal, but
agreement is *not* a correctness proof. The effect also concentrates on the two hardest twists (`gap`,
`bracket`); the other four had zero disagreements, so diversity added nothing there.

## Closing the learning loop (on a REAL external signal)

The honest weakness of v2's learning loop was its default *self*-score. [`engine/close_loop.py`](engine/close_loop.py)
closes it on the one signal with measured, significant variance — the Benchmark-1 population-diversity
scores (archive vs baseline, p<0.0001), an objective embedding metric, never a model grading itself:

- Train the playbook on **half** the trials' external diversity scores → it recommends **`archive`** for
  `maximize_diversity`.
- On the **held-out** half, `archive` is indeed best (0.855 vs baseline 0.623) — the learned choice
  **generalizes out-of-sample**, beating baseline by **+0.232** and a random strategy by **+0.141**.

That is the engine measurably *becoming better*: routing learned from external data and validated out of
sample, not asserted. (The loop is signal-agnostic — give it pass/fail or human ratings and it improves on
those instead; we just don't have a non-saturated accuracy signal to feed it, per Benchmark 4.)

## What remains genuinely open

Benchmarks 1–4 establish: mode collapse is real (B1) and structure escapes it (B1 archive, generalized in
the closed loop); the engine diversifies the solution space (B2) and routes the right mode per problem (B3);
and properly measured, there is **no pass@k headroom** for the engine to convert into an accuracy win on
construct-and-check tasks at this model's strength (B4). The honest frontier left is exactly the thing that
stayed out of reach all session: **tasks a frontier model genuinely cannot solve single-pass yet are
checkable with a trusted oracle** (research-level, or very long-horizon), plus a **cross-family judge** for
open-ended quality. Those are the conditions under which "more kinds of thinking" could show an accuracy
win — and we did not pretend to have them.

---
### (historical) the pass@k test, before we ran it

Benchmark 2 showed the engine diversifies the solution space on *easy* problems (correctness saturated).
The decisive remaining test was whether that diversity *pays off on HARD problems where the baseline fails*: a compute-matched **pass@k coverage** benchmark on verifiable tasks with real
headroom (pass@1 < 1), out to large k, with the unbiased estimator and a dumb-guessing control, per
[`BENCHMARKING.md`](BENCHMARKING.md) P5. That is where "more distinct correct solutions" becomes "solves
problems a predictor can't." It needs a curated hard-problem set with trusted oracles and a real token
budget — scoped and specified, not yet run at scale. A blind, length-controlled ideation comparison is the
other open step, gated on a **cross-family judge** so it stays honest (we only have Claude here). We flag
these rather than over-claim: Benchmarks 1–2 establish that mode collapse is real and that structure
escapes it; they do **not** yet establish a problem-solving win on hard tasks.

## Reproduce

```bash
python bench/score.py            # scorer self-check
python bench/run_dat.py          # Benchmark 1 (DAT), from bench/data/dat_raw.json
python bench/run_code.py         # Benchmark 2 (coding diversity), from bench/data/code_raw.json
python bench/recheck_methodology.py   # re-verify the methodology citations
```
