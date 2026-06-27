# Demo: diversity as a correctness oracle (differential testing)

*The first place the engine shows a measured advantage on **correctness**, not just diversity. Captured
from `bench/fuzz_eval.py` (2000 adversarial inputs/problem) over the already-generated twisted-problem
solutions — and reproduced as a reusable capability in [`engine/diff_test.py`](../engine/diff_test.py).*

## The setup

The pass@k benchmark ([Benchmark 4](../RESULTS.md)) used ~26 fixed inputs per problem and showed a
near-perfect ceiling. But a small fixed test set can *miss rare bugs*. So we re-ran every generated
solution against **2000 random inputs** per problem, checked against the trusted brute reference.

## What fuzzing revealed

- **The ceiling was slightly optimistic.** 2 of 72 solutions (one `gap`, one `bracket`) **passed the
  fixed tests but FAIL under fuzzing** — subtle bugs the weak test set never triggered.
- **Diversity is a correctness oracle.** Pooling the diverse solutions and flagging inputs where they
  *disagree* exposed **383 bug-revealing inputs — with no reference solution at all**.
- **Majority vote recovered the right answer on 383 / 383 = 100%** of those disagreement cases.
- A single forward pass ships a buggy solution on **~0.33%** of inputs (and ~1 in 36 solutions harbors
  such a bug); the engine's diverse-generate → differential-test → majority-vote catches and corrects it.

## Two concrete bugs caught (found before the reference confirmed them)

| problem | input | diverse outputs | majority (shipped) | reference | verdict |
|---|---|---|---|---|---|
| `gap` | `num_gap_subseq("abaaa", "aa")` | 11×**4**, 1×2 | **4** | 4 | buggy minority outvoted ✓ |
| `bracket` | `longest_valid("([()][[]")` | 11×**4**, 1×6 | **4** | 4 | buggy minority outvoted ✓ |

For `gap`, the non-adjacent subsequences of `abaaa` equal to `aa` are indices (0,2),(0,3),(0,4),(2,4) = **4**;
the one buggy solution returns 2. The disagreement *is* the bug detector — the engine never needed the
reference to know something was wrong.

## Why this matters (and its honest limit)

A single forward pass is confidently alone: if it writes the rare buggy variant, it ships it. The engine
samples several *structurally different* solutions, and their **disagreement is a free correctness signal**
— exactly the diversity thesis paying off where pass@1 couldn't show it.

> **Honest limit:** this catches *idiosyncratic* (minority) bugs. If most candidates share the **same**
> wrong belief (a systematic error), the majority is wrong and diversity can't save you. So a disagreement
> is a strong "investigate this" signal, but **agreement is not a proof of correctness.** `engine/diff_test.py`
> says so in its own output.
