---
name: divergence
description: >
  Turn a coding/ideation task from a predictable answer into a genuinely novel one. Use when the user
  wants ideas that are "outside the box", a non-obvious design/approach/architecture, to break out of
  repetitive or generic suggestions, or explicitly invokes /diverge. Runs a 6-stage divergence loop
  (escape the mode → spread → recombine → search → adversarially verify → frontier-select) grounded in
  the divergent-agents research. SKIP for mechanical edits where the obvious answer is the right one.
---

# Divergence Engine

You are running a search whose job is to escape the *mode* of your own distribution — the predictable
answer — and return something novel **and** correct. A single forward pass samples the mode; this loop
does not. Novelty metric: the bundled `novelty.py` (ships inside this skill folder).

## When to run / when to skip
- **Run** when novelty is the goal: design, architecture, naming, product ideas, research directions,
  algorithm choice, "we keep landing on the same thing", or an explicit `/diverge`.
- **Skip** (just answer) for mechanical edits, lookups, or when the conventional answer is demonstrably
  correct. Divergence costs compute — don't spend it where the mode is right. Say you're skipping and why.
- **Escalate** to the fan-out harness `harness/divergence_engine.js` (real parallel subagents per lens +
  refuter) when the task is high-stakes or the inline version keeps collapsing. Run it with the Workflow tool.

## The protocol — do every stage, in order, visibly

### 0 · Name the Mode
State the **single most predictable answer** — what a competent-but-unimaginative agent would output
here. One or two sentences. This is your baseline-to-beat; you are not allowed to ship it as the answer.

### 1 · Tail Sampling — generate ≥5 structurally different candidates
Use **verbalized sampling** + **forced lenses**. Write each candidate with a self-estimated
*conventionality* p (0 = nobody does this, 1 = everybody does), and deliberately mine the low-p tail:

> "Give me ≥5 distinct approaches to <task>. For each: a one-line summary and a conventionality
>  probability p. At least 3 must have p < 0.3."

Each candidate must come from a **different lens** — do not reuse a lens:
- **Analogy**: solve it the way a *different domain* does (biology, logistics, games, finance, physics…).
- **Step-back**: abstract to the general principle, then re-specialize differently.
- **Invert the constraint**: what if the thing everyone treats as fixed is the variable?
- **First principles**: rederive from scratch, ignoring how it's "normally" done.
- **Blend**: fuse two unrelated existing solutions into one.
- **Remove / exaggerate** (SCAMPER): delete the "essential" part; or push one dimension to 100×.

### 2 · Novelty gate (kill the paraphrases)
Run the candidate set through the bundled metric (`novelty.py` ships in this skill folder — run from there,
or copy `novelty.py` next to `cands.json`):
```bash
python -c "import novelty, json; c=json.load(open('cands.json')); \
print('set_diversity=%.3f'%novelty.set_diversity(c)); print('diverse pick:', novelty.select_diverse(c, 3))"
```
(Write the candidate one-liners to `cands.json` as a JSON list first.) If `set_diversity < 0.5`, your
"different" ideas are paraphrases of the mode — **go back to stage 1** with a ban-list ("do NOT propose
anything close to: …") and harder lenses. Keep the `select_diverse` spread, drop near-duplicates.
Maintain an **archive** of everything proposed this session so you never re-offer it.

### 3 · Recombine
Take the 2–3 most *distant* survivors and breed them: "What does the hybrid of A and B look like?"
Produce hybrids that neither parent contained. Add the good ones to the pool.

### 4 · Deepen the survivors
For the top 2–3, expand each into a short branch-and-evaluate: sketch how it actually plays out, where
it could fork, and backtrack from dead ends. Spend the most effort on the most promising branch — don't
commit greedily to the first.

### 5 · Adversarial verification (novel AND correct)
For each survivor, **switch hats and try to break it**: correctness, feasibility, hidden cost, why it
might fail. If the work is executable (code, a formula, a testable claim) — **actually run it / check it**;
an external signal beats self-critique. Kill anything that doesn't survive. Self-praise is not verification.

### 6 · Frontier select
Pick the candidate that is **most novel among those that clear the quality bar** — rare-and-good beats
common-and-good. Don't default to the safest. Synthesize the winner (optionally grafting the best idea
from a runner-up). Then deliver:

- **The pick** and how to do it.
- **Why it beats the mode** (the Stage-0 baseline) — explicit novelty + value delta.
- **Honest risk** — the strongest objection from Stage 5 and how it's handled.
- *(optional)* the 1–2 runners-up, in a line each, so the user can see the road not taken.

## Anti-collapse reflexes (run throughout)
- If your candidates start agreeing or your confidence spikes early, that's the mode pulling you back —
  **inject a counter-pressure idea** before committing.
- Never trust a single generation for an open-ended subtask; sample, then select.
- Protect "fork" decisions (which approach/file/hypothesis) — re-sample alternatives there instead of
  taking the greedy choice.
