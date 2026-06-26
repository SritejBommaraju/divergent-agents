# divergent-agents

**Turning general-purpose coding agents (Claude Code, Codex) from next-move *predictors* into *divergent thinkers*.**

> Today's LLM agents are trained to predict the single most-likely next move. That makes them
> reliable and *trapped*: they converge on the obvious answer and rarely push past it. This repo
> is a research-and-build effort to give a coding agent a **harness** — a skill / agent loop — that
> makes it deliberately explore, recombine, and pressure-test ideas so it produces work that is
> genuinely novel, not merely competent.

## The thesis

A single forward pass is an exploitation move: it samples near the mode of the training
distribution. "Thinking outside the box" is an **exploration** problem. You don't get it by asking
the model to "be creative" — you get it by wrapping the model in a *process* that:

1. **Forces divergence** before convergence (generate many structurally-different candidates, not one).
2. **Rewards novelty explicitly** (keep an archive of stepping-stones; penalize sampling near what's
   already been tried — the Quality-Diversity / Novelty-Search insight).
3. **Searches** a branching solution space instead of committing to a greedy chain.
4. **Recombines** across domains (analogy / conceptual blending) to leave the in-distribution rut.
5. **Adversarially verifies** so divergence doesn't degrade into nonsense — novel *and* correct.
6. **Measures** outside-the-box-ness so the loop can optimize for it and we can prove it works.

Every one of those moves is grounded in peer-reviewed / arXiv literature. See [`research/`](research/).

## Repo layout

| Path | What |
|---|---|
| `research/REPORT.md` | Master report — every method, every paper, each one **verified real** against the arXiv / Semantic Scholar APIs. |
| `research/by-theme/` | Per-theme deep dives (mode collapse, decoding, quality-diversity, evolution, search, reflection, idea-generation, analogy, evaluation, RL-exploration). |
| `research/verification.md` | The independent citation-verification log (which IDs resolved, which were corrected/dropped). |
| `skill/` | The deliverable: a Claude Code skill/harness that operationalizes the findings. |
| `src/` | Supporting code (novelty metric, candidate-diversity check). |

## Status

🔬 Research in progress. Reports are generated from a verified-research pipeline: a fan-out of
per-theme scouts, each followed by a strict citation-verifier that re-fetches every paper from the
arXiv / Semantic Scholar APIs. No citation lands in a report without an independent existence check.

## Principle

Ambition over caution. The goal is not "an agent that is competent" — it's an agent whose output
*stops you in your tracks*. Difficulty is the specification, not a deterrent.
