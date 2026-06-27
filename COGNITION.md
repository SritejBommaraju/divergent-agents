# The Cognitive Engine — from one kind of thinking to the most kinds

*v2 of the [Divergence Engine](METHOD.md). Grounded in the verified thinking-modes research
([`research/thinking-modes/REPORT.md`](research/thinking-modes/REPORT.md) — 36 papers, all re-checked).*

## Why v1 wasn't enough

The Divergence Engine does **one** kind of thinking superbly: divergent breadth (generate many,
recombine, verify). But [Benchmark 1](RESULTS.md) showed that *divergence prompting is sometimes a
null* — on word-naming it didn't beat the baseline at all. And most real problems don't want breadth:
a proof wants **deduction**, a bug wants **abduction**, a Fermi estimate wants **decomposition +
Bayesian** reasoning, a trade-off wants **dialectic**. A system that always brainstorms is a
one-trick pony wearing a lab coat.

> "The most kinds of thinking" is not a bigger hammer. It's a **toolbox plus the judgment to pick the
> right tool** — a library of reasoning modes and a metacognitive router over them.

## Architecture

```
            ┌──────────── learning loop (engine/learn.py + playbook.json) ────────────┐
            │  records {task_type, plan, score}; biases future routing toward winners   │
            v                                                                            │
  TASK ──► ROUTER ──► [mode₁ ─► mode₂ ─► … ─► convergent_verify] ──► SYNTHESIS ──► answer + record ──┘
        (metacognition)        (sequential mode operators, each building on the last)
```

1. **Mode library** ([`engine/modes.json`](engine/modes.json)) — 12 reusable thinking-mode operators,
   each with a *trigger* (when it's needed), a *protocol* (the steps), and a *grounding* paper.
2. **Router** — a metacognitive controller diagnoses the task and composes a *minimal ordered
   sequence* of modes (not always divergence), always ending in verification. Grounded in **Self-Discover**
   ([arXiv:2402.03620](https://arxiv.org/abs/2402.03620)), which showed composing atomic reasoning
   modules per task beats any fixed prompt.
3. **Sequential execution** — each mode runs its protocol, feeding its load-bearing result forward.
4. **Convergent verification** — always last: re-derive + adversarially refute + (if executable) run.
5. **Learning loop** — every run emits a record; the playbook accumulates which mode-plans work per
   task type, so routing improves over time (the "keep becoming better" mechanism).

## The grounded mode library

| Mode | Family | When | Grounded in |
|---|---|---|---|
| divergent | divergent | open design / novelty | ToT ([2305.10601](https://arxiv.org/abs/2305.10601)) |
| decompose | decompositional | complex multi-step | Least-to-Most ([2205.10625](https://arxiv.org/abs/2205.10625)), Plan-and-Solve ([2305.04091](https://arxiv.org/abs/2305.04091)) |
| deductive | deductive | rules/proof/entailment | Selection-Inference ([2205.09712](https://arxiv.org/abs/2205.09712)), LAMBADA ([2212.13894](https://arxiv.org/abs/2212.13894)) |
| inductive | inductive | examples → rule | Hypothesis Search ([2309.05660](https://arxiv.org/abs/2309.05660)), HtT ([2310.07064](https://arxiv.org/abs/2310.07064)) |
| abductive | abductive | diagnosis / root-cause | Inference to Best Explanation ([2402.10767](https://arxiv.org/abs/2402.10767)) |
| analogical | analogical | stuck / cross-domain | Analogical Reasoners ([2310.01714](https://arxiv.org/abs/2310.01714)) |
| first_principles | first-principles | challenge the obvious | Step-Back ([2310.06117](https://arxiv.org/abs/2310.06117)) |
| causal | causal | cause / intervention / counterfactual | causal-reasoning literature |
| bayesian | probabilistic | uncertainty / estimation | probabilistic-reasoning literature |
| dialectic | dialectical | trade-off / contested | Multi-agent debate ([2305.14325](https://arxiv.org/abs/2305.14325)) |
| convergent_verify | convergent | finalize / check | Self-Consistency ([2203.11171](https://arxiv.org/abs/2203.11171)), Deductive Verification ([2306.03872](https://arxiv.org/abs/2306.03872)) |
| metacognitive | metacognitive | high uncertainty / route | Self-Discover ([2402.03620](https://arxiv.org/abs/2402.03620)) |

Full operator protocols + 36 verified papers: [`research/thinking-modes/REPORT.md`](research/thinking-modes/REPORT.md).

## Evidence (and where it's honestly a null)

**The router genuinely differentiates — it is not a one-trick pony** ([`demos/02-router-differentiation.md`](demos/02-router-differentiation.md)).
Across 10 varied tasks the router produced **9 distinct mode-plans** with **8 distinct primary modes** —
deploying divergence *only* for the two genuinely open tasks and routing diagnosis → abduction, proof →
deduction, estimation → decompose+Bayesian, trade-off → dialectic, etc. This is the core capability: the
engine selects the kind of thinking the problem needs.

**On accuracy, strategy is a ceiling-bound null — and we say so.** On every reasoning task we could both
*construct and check* (logic, Bayesian, combinatorics, induction, arithmetic, code), a frontier model
scored **100% under baseline, always-divergent, AND router alike** ([Benchmark 4 in RESULTS.md](RESULTS.md)).
The honest reading: for a strong model on *solvable* problems, the thinking *strategy* doesn't change
*accuracy* — the model already knows the answer. (We also caught and fixed a grading artifact where
verbose answers were penalized for *mentioning* distractor tokens — a reminder that the checker is part
of the experiment.) The value of "more kinds of thinking" is therefore **not** higher accuracy on
solvable tasks; it is **breadth, adaptivity, solution-space coverage** ([Benchmark 2](RESULTS.md): the
engine yields 9× more distinct correct solutions), and **not regressing** while doing so.

## Honest limitations

- **No demonstrated accuracy win over a strong model thinking hard.** Routing helps weaker models and
  structured tasks in the literature; for a frontier model on solvable tasks we measured a null. We do
  not claim otherwise.
- **The learning loop's default signal is self-assessed** (a model grading itself = weak). `engine/learn.py`
  prefers *external* signals and labels the source so the two are never silently mixed. The strong version
  is **demonstrated** in [`engine/close_loop.py`](engine/close_loop.py): trained on the real, objective
  Benchmark-1 diversity signal it learns `maximize_diversity → archive`, and that choice **generalizes
  out-of-sample** (held-out diversity 0.855 vs baseline 0.623, +0.232). See [RESULTS.md](RESULTS.md).
- **Routing adds latency and cost**; for trivial tasks it's overkill (the engine should — and the skill
  does — skip straight to answering).
- **Mode boundaries overlap** (causal vs abductive, first-principles vs divergent); the router sometimes
  picks reasonable-but-arguable sequences.

## What it delivers

Breadth (12 grounded modes vs 1), demonstrated adaptivity (right mode per problem), composability (the
v1 Divergence Engine is now just *one mode* in the library), no accuracy regression, and a learning
substrate to improve routing over time — honestly scoped to where the evidence supports it.
