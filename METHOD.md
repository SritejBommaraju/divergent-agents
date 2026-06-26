# The Divergence Engine — a method for turning a coding agent from a predictor into a thinker

*Grounded end-to-end in the 78 verified papers in [`research/REPORT.md`](research/REPORT.md). Every
claim below links to a paper that was independently confirmed real (see
[`research/verification.md`](research/verification.md)).*

---

## 1. The problem, stated precisely

A base or aligned LLM, run as a single forward pass, is a **mode-seeking** system: it puts its
probability mass on the most *typical* continuation and samples near it. That is exactly what you
want for "rename this variable" and exactly what traps it on "design something nobody has tried."

Two findings make this concrete and show it is not a vibe but a measurable property of the models we
deploy:

- **Alignment sharpens the distribution and kills diversity.** RLHF improves out-of-distribution
  generalisation but *significantly reduces* per-input output diversity versus SFT — a measured
  generalisation-vs-diversity tradeoff ([Understanding the Effects of RLHF…, arXiv:2310.06452](https://arxiv.org/abs/2310.06452)).
  The cause reaches below the algorithm into the *data*: human preference annotators favor familiar,
  conventional text ("**typicality bias**"), so preference tuning teaches the model to be typical
  ([Verbalized Sampling, arXiv:2510.01171](https://arxiv.org/abs/2510.01171)).
- **The result is "attractor states."** Aligned models show lower token-prediction entropy and fall
  back to a small set of repeated outputs across independent calls
  ([Creativity Has Left the Chat, arXiv:2406.05587](https://arxiv.org/abs/2406.05587)) — which is
  why naively asking an agent for "another idea" returns a paraphrase of the first.

So: **the predictor isn't broken; it's doing its job.** Outside-the-box output is not a better
forward pass — it is an *exploration* problem layered on top of an exploitation engine.

> **Thesis.** Intelligence we'd call "thinking" does not live in the forward pass. It lives in the
> **loop around it** — a search whose operators are tuned to escape the mode, and whose gate keeps
> only what survives refutation. The Divergence Engine is that loop.

## 2. Why the obvious fixes are not enough (and what the literature says instead)

| Tempting fix | What the research actually shows | Consequence for the design |
|---|---|---|
| "Just tell it to be creative / raise temperature." | High temperature alone trades coherence for diversity and produces repetition/garbage; you need *adaptive* truncation ([min-p, arXiv:2407.01082](https://arxiv.org/abs/2407.01082); [Locally Typical Sampling, arXiv:2202.00666](https://arxiv.org/abs/2202.00666)). | Decoding control is a *layer*, not the method; and on a hosted aligned model you often can't set it — so divergence must also work at the *prompt/loop* level. |
| "Let it critique and refine itself." | Self-critique reliably improves *surface quality* but does **not** generate genuinely new hypotheses; without an external signal it collapses to consensus — "[LLMs Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798)". | Reflection is for *verification*, not *divergence*; and verification needs an **external/adversarial** signal to be trusted. |
| "Sample many and pick the best." | Coverage rises with samples (self-consistency, best-of-N, test-time scaling) — but a *quality-only* ranker re-selects the mode, and ideation novelty saturates into duplicates ([Can LLMs Generate Novel Research Ideas?, arXiv:2409.04109](https://arxiv.org/abs/2409.04109)). | Need an explicit **novelty archive** to deduplicate and a **frontier** selector so ranking doesn't undo the divergence. |
| "More RL / reasoning training." | RL often *sharpens* an existing skill rather than expanding the reasoning boundary beyond the base model, and can *collapse* policy entropy ([arXiv:2504.13837](https://arxiv.org/abs/2504.13837); [The Entropy Mechanism, arXiv:2505.22617](https://arxiv.org/abs/2505.22617)). | Exploration must be *actively protected* at decision points, not assumed. |

The Engine is the composition that closes each of these gaps at once. No single paper does that — the
contribution here is the **integration into one agent loop with an anti-collapse control system.**

## 3. The architecture — six stages + a control system

```
            ┌───────────────────────────── collapse monitor / curiosity gate ─────────────────────────────┐
            │  (entropy & inter-candidate agreement; protect "fork" decisions; spend exploration budget)    │
            v                                                                                                │
 [0] Name the Mode → [1] Tail Sampling → [2] Novelty Archive → [3] Recombination → [4] Deepen by Search → [5] Adversarial Verify → [6] Frontier Select
        (anti-typicality)   (verbalized+lensed)   (QD dedupe gate)    (LLM crossover)      (ToT/LATS)          (novel AND correct)     (novelty×value)
            │                                          ^                                                                                    │
            └───── if diversity < threshold: regenerate stage 1 with ban-list + harder constraints ─────────┘ (loop)                       v
                                                                                                                                       winner + why-it-beats-the-mode
```

### Stage 0 — Name the Mode  *(anti-typicality framing)*
Before solving, the agent writes down the **predictable answer** — the mode of its own distribution —
and commits to beating it. This converts the typicality bias from an invisible default into an
explicit baseline-to-exceed.
*Grounds:* typicality bias ([2510.01171](https://arxiv.org/abs/2510.01171)); attractor states
([2406.05587](https://arxiv.org/abs/2406.05587)). *Prevents:* silently shipping the modal answer.

### Stage 1 — Tail Sampling  *(verbalized + lensed divergence)*
Generate N **structurally distinct** candidates, two mechanisms stacked:
- **Verbalized sampling** — ask for N approaches *each with a self-estimated "conventionality
  probability,"* then deliberately work the low-probability tail. This is the single most actionable,
  training-free lever; it recovers the latent diversity alignment suppressed (1.6–2.1× diversity
  gains) ([2510.01171](https://arxiv.org/abs/2510.01171)).
- **Forced lenses** — each candidate must come from a *different* operator: a cross-domain analogy
  ([Analogical Reasoners, arXiv:2310.01714](https://arxiv.org/abs/2310.01714)), an abstraction/step-back
  ([Take a Step Back, arXiv:2310.06117](https://arxiv.org/abs/2310.06117)), a constraint inversion, a
  first-principles rederivation, or a conceptual blend ([PopBlends, arXiv:2111.04920](https://arxiv.org/abs/2111.04920)).
- *Decoding layer (when controllable):* high temperature guarded by min-p
  ([2407.01082](https://arxiv.org/abs/2407.01082)) or diverse beam search
  ([1610.02424](https://arxiv.org/abs/1610.02424)).

*Prevents:* N paraphrases of the mode.

### Stage 2 — Novelty Archive  *(quality-diversity dedupe gate)*
Score the *set* for structural diversity and each candidate's novelty against an **archive of
everything tried** (this session + persisted). Drop near-duplicates; keep an *illuminated spread*
across a behavior space rather than k clones. If diversity < threshold, **regenerate Stage 1** with a
ban-list of prior outputs and harder constraints.
*Grounds:* Novelty Search ([Abandoning Objectives, EVCO 2011](https://doi.org/10.1162/EVCO_a_00025));
MAP-Elites ([1504.04909](https://arxiv.org/abs/1504.04909)); Quality-Diversity through AI Feedback
([2310.13032](https://arxiv.org/abs/2310.13032)); NoveltyBench ([2504.05228](https://arxiv.org/abs/2504.05228)).
*Implemented by* [`src/novelty.py`](src/novelty.py). *Prevents:* collapse back onto the attractor.

### Stage 3 — Recombination  *(LLM as crossover operator)*
Take the most **distant** survivors and breed them — conceptual blends / evolutionary crossover — to
produce hybrids no single candidate contained. Ideation is a *population that breeds*, not a one-shot.
*Grounds:* Evolution through Large Models ([2206.08896](https://arxiv.org/abs/2206.08896)); Language
Model Crossover ([2302.12170](https://arxiv.org/abs/2302.12170)); FunSearch
([Nature 2024](https://www.nature.com/articles/s41586-023-06924-6)); AlphaEvolve
([2506.13131](https://arxiv.org/abs/2506.13131)); Promptbreeder ([2309.16797](https://arxiv.org/abs/2309.16797));
OPRO ([2309.03409](https://arxiv.org/abs/2309.03409)). *Prevents:* leaving cross-pollination on the table.

### Stage 4 — Deepen by Search  *(tree search + test-time compute)*
Expand each remaining candidate into a small reasoning tree with **backtracking** and a value
estimate; pour more compute into the promising branches instead of committing to a greedy chain.
*Grounds:* Tree of Thoughts ([2305.10601](https://arxiv.org/abs/2305.10601)); Graph of Thoughts
([2308.09687](https://arxiv.org/abs/2308.09687)); LATS ([2310.04406](https://arxiv.org/abs/2310.04406));
Self-Consistency ([2203.11171](https://arxiv.org/abs/2203.11171)); test-time scaling
([2408.03314](https://arxiv.org/abs/2408.03314)). *Prevents:* a locally-greedy chain killing a good branch.

### Stage 5 — Adversarial Verification  *(novel AND correct — the load-bearing guard)*
Each survivor faces a **refuter** tasked to break it (correctness, feasibility, hidden cost) plus an
**external/objective check where one exists** (run the code, the test, the evaluator). Kill what
doesn't survive. This is non-negotiable: the literature is unambiguous that self-critique without an
external signal does not help, and that *novel* ideas are systematically rated *less feasible* —
there is a real **ideation-execution gap**.
*Grounds:* LLMs Cannot Self-Correct ([2310.01798](https://arxiv.org/abs/2310.01798)); Reflexion
([2303.11366](https://arxiv.org/abs/2303.11366)) and Self-Refine ([2303.17651](https://arxiv.org/abs/2303.17651))
*work with a signal*; Multiagent Debate ([2305.14325](https://arxiv.org/abs/2305.14325)); The
Ideation-Execution Gap ([2506.20803](https://arxiv.org/abs/2506.20803)); novel-but-less-feasible
([2409.04109](https://arxiv.org/abs/2409.04109)). *Prevents:* confident nonsense; divergence rotting into wrongness.

### Stage 6 — Frontier Select  *(novelty × value, not value alone)*
Choose the point on the **Pareto frontier** that maximizes novelty *subject to a quality floor* —
operationalizing "**rare-and-good beats common-and-good**." Synthesize the winner, optionally grafting
the best ideas of runners-up, and state explicitly why it beats the Stage-0 mode.
*Grounds:* Diverse Preference Optimization ([2501.18101](https://arxiv.org/abs/2501.18101)); Creative
Preference Optimization ([2505.14442](https://arxiv.org/abs/2505.14442)); Measuring LLM Novelty
([2504.09389](https://arxiv.org/abs/2504.09389)); Rethinking Creativity Evaluation
([2508.05470](https://arxiv.org/abs/2508.05470)). *Prevents:* a quality-only ranker quietly re-selecting the mode.

### Control system — collapse monitor & curiosity gate (runs across all stages)
Track inter-candidate agreement / output entropy as a live proxy for *exploration vanishing*. When
the agent's confidence is suspiciously high, or critics agree too fast, **spend extra exploration
budget** and protect high-leverage "fork" decisions (which algorithm? which file? which hypothesis?)
from premature commitment.
*Grounds:* The Entropy Mechanism ([2505.22617](https://arxiv.org/abs/2505.22617)); RL-vs-base-model
boundary ([2504.13837](https://arxiv.org/abs/2504.13837)); Pass@k Training ([2508.10751](https://arxiv.org/abs/2508.10751));
Curiosity-Driven Exploration ([CDE, arXiv:2509.09675](https://arxiv.org/abs/2509.09675)); Reasoning with
Exploration ([2506.14758](https://arxiv.org/abs/2506.14758)).

## 4. What makes this a *thinker* and not a fancier predictor

A predictor answers from the mode. The Engine, by construction:
1. **starts** by refusing the mode (Stage 0–1),
2. **remembers** what's been tried and won't repeat it (Stage 2 archive),
3. **breeds** new combinations rather than retrieving one (Stage 3),
4. **searches** instead of committing (Stage 4),
5. **submits its ideas to refutation and reality** (Stage 5), and
6. **prefers the rare-good over the common-good** (Stage 6),
   while a **control loop** notices when it is collapsing and pushes back.

That sequence — escape → don't-recollapse → recombine → search → refute → frontier-select — is the
operational definition of "understanding over predicting" we set out to build.

## 5. How we prove it works (not just assert it)

- **Novelty metric** in [`src/novelty.py`](src/novelty.py): structural diversity of a candidate set,
  novelty-vs-archive, and max-min diverse selection (lexical now; embedding-swap upgrade documented).
- **Pass@k mindset**, not pass@1: score by *coverage of distinct correct solutions* across attempts
  ([2504.13837](https://arxiv.org/abs/2504.13837); [2408.03314](https://arxiv.org/abs/2408.03314)).
- **A/B against the Stage-0 mode**: every run records the modal baseline and the chosen output's
  novelty×quality delta, so "outside the box" is a measured number, not a claim
  ([NoveltyBench 2504.05228](https://arxiv.org/abs/2504.05228); [Ocsai, TSC 2023](https://doi.org/10.1016/j.tsc.2023.101356)).

## 6. Honest limitations (named, with the path through — not used to back off)

- **Semantic novelty is the hard part.** The shipped metric is *lexical* (character n-gram distance):
  cheap and dependency-free, but a clever paraphrase can fool it. *Path:* swap the single `distance()`
  function for embedding cosine distance; every other function is distance-agnostic. The harness already
  gates on it, so the upgrade is a one-line change.
- **Hosted aligned models cap their own diversity.** When we can't set decoding params, Stage 1 leans
  on verbalized sampling + lenses, which help but don't fully restore base-model entropy. *Path:*
  expose a decoding profile when running against a controllable endpoint (min-p + temperature).
- **Refuters are also LLMs.** Stage 5 is only as trustworthy as its *external* signal. For executable
  work (code, proofs, evaluable functions) it is strong — run it. For non-executable ideation it is
  weaker; we mitigate with adversarial, perspective-diverse refuters and an explicit feasibility score,
  but flag residual risk rather than hide it.
- **It costs compute and latency.** The Engine is overkill for mechanical edits. *Path:* a stakes gate
  — trivial tasks skip straight to the forward pass; the Engine is invoked only when novelty is the goal.

## 7. Two instantiations (same method)

- **Inline skill** — [`skill/divergence/SKILL.md`](skill/divergence/SKILL.md): the agent runs the six
  stages itself within a turn. Zero infra; works in any Claude Code / Codex session.
- **Fan-out harness** — [`harness/divergence_engine.js`](harness/divergence_engine.js): the
  turbocharged version that spawns real parallel subagents per lens and per refuter via the Workflow
  primitives — true population-based divergence with adversarial verification.
