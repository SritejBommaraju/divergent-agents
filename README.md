# divergent-agents

**Turning general-purpose coding agents (Claude Code, Codex) from next-move *predictors* into *divergent thinkers*.**

> Today's LLM agents are trained to predict the single most-likely next move. That makes them
> reliable and *trapped*: they converge on the obvious answer and rarely push past it. This repo
> is a research-and-build effort that (a) surveys — and **verifies real** — every method we could find
> for escaping that trap, and (b) ships a working **harness** (skill + fan-out engine) that makes a
> coding agent deliberately explore, recombine, and pressure-test ideas so its output is genuinely
> novel, not merely competent.

## The thesis

A single forward pass is an *exploitation* move — it samples near the mode of the training
distribution. "Thinking outside the box" is an *exploration* problem, and you don't get it by asking
the model to "be creative." You get it by wrapping the model in a **process** that escapes the mode,
refuses to re-collapse, recombines, searches, and verifies. The full argument, grounded paper-by-paper,
is in **[`METHOD.md`](METHOD.md)**.

> **Intelligence we'd call "thinking" does not live in the forward pass. It lives in the loop around it.**

## What's inside

| Path | What |
|---|---|
| **[`METHOD.md`](METHOD.md)** | The **Divergence Engine** — the method. A 6-stage agent loop + a collapse-monitor control system, each stage grounded in verified literature. **Start here.** |
| **[`BENCHMARKING.md`](BENCHMARKING.md)** | The **best honest tactic** for benchmarking divergence — 5 principles + traps, from 23 verified methodology papers. How not to fool yourself. |
| **[`RESULTS.md`](RESULTS.md)** | **What the benchmark found** — including where the engine *fails*. The honest edition. |
| [`bench/`](bench/) | The benchmark harness: objective embedding-ensemble scorer, stats (bootstrap + permutation), raw data, re-verification scripts. |
| [`skill/divergence/SKILL.md`](skill/divergence/SKILL.md) | The **inline harness** — a `/diverge` Claude Code skill the agent runs itself in any session. |
| [`harness/divergence_engine.js`](harness/divergence_engine.js) | The **fan-out harness** — the turbocharged engine that spawns real parallel subagents per lens + per refuter (run with the Workflow tool). |
| [`demos/01-self-collapse-detector.md`](demos/01-self-collapse-detector.md) | A **real run, captured verbatim** — the engine designing a hard mechanism, with every divergent candidate adversarially refuted and a surviving winner synthesized. |
| [`research/REPORT.md`](research/REPORT.md) | **Master report** — 78 papers across 10 themes; every one linked and **independently verified real**. |
| [`research/by-theme/`](research/by-theme/) | Per-theme deep dives. |
| [`research/verification.md`](research/verification.md) | The citation-verification ledger (two independent sources; 78/78). |
| [`research/papers.json`](research/papers.json) | Machine-readable record of every paper + its verification fields. |
| [`src/novelty.py`](src/novelty.py) | The novelty/diversity metric the harness gates on (lexical now, embedding-ready). |

## Results so far

- **78 / 78 papers verified real** across 10 themes — checked twice, by independent means (arXiv API
  in-pipeline, then a Semantic Scholar batch + Crossref re-check). **Zero fabricated citations.** See
  [`research/verification.md`](research/verification.md).
- **A working harness, demonstrated end-to-end.** In [the captured run](demos/01-self-collapse-detector.md)
  the engine named the obvious answer, generated 6 structurally-different alternatives (set-diversity
  0.81), had **all** of them torn apart by adversarial verifiers, and synthesized a winner that
  survives the exact objections that sank the rest — landing somewhere a single forward pass never would.
- **Two benchmarks with honest findings** ([`RESULTS.md`](RESULTS.md)):
  - *Divergent Association Task:* **prompting an LLM to "be divergent" did nothing** (p=0.84) — it just
    relocates the cliché vocabulary (`volcano`→`grief`). The engine's **structural** Stage-2 memory
    (cross-response novelty archive) lifted *population* diversity **+0.229 (p<0.0001), no quality loss**.
  - *Coding:* best-of-N collapses to **one** algorithm (10/10 identical `fib`; 1.33 distinct/10 across
    problems); the engine's lenses yield **9.33 distinct correct algorithms** — 7× the solution-space
    coverage, 30/30 still correct.
  - The honest synthesis: divergence lives in the **loop**, not the forward pass — and "be creative"
    prompting only helps when the task has a structured strategy space to point at. Measured, not asserted.

## Quickstart

**Run the metric self-check** (no deps):
```bash
python src/novelty.py        # lexical novelty/diversity gate + self-check
```

**Use the inline skill** in Claude Code: copy the skill into your skills dir, then invoke `/diverge`:
```bash
cp -r skill/divergence ~/.claude/skills/        # or  .claude/skills/  for project scope
# then in a session:  /diverge <your task>
```

**Run the fan-out engine** (real parallel subagents) with the Workflow tool:
```js
Workflow({ scriptPath: "harness/divergence_engine.js",
           args: { task: "<your task>", lenses: 6, survivors: 3, refuters: 3 } })
```

**Reproduce the verification**:
```bash
python src/recheck_s2.py     # Semantic Scholar batch re-check  -> research/s2_recheck.json
python src/gen_reports.py    # regenerate all reports from the research run
```

## Principle

Ambition over caution. The goal is not "an agent that is competent" — it's an agent whose output
*stops you in your tracks*. Difficulty is the specification, not a deterrent.
