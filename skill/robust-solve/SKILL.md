---
name: robust-solve
description: >
  Write CORRECT code by cross-checking diverse solutions, not by trusting one. Use when correctness
  matters and a subtle bug would be costly (algorithms, parsers, financial/Date logic, anything with
  nasty edge cases), or when the user invokes /robust-solve. Generates several structurally-different
  solutions, fuzz-tests them against each other (differential testing), and ships the consensus —
  catching the rare bug a single forward pass would ship undetected. SKIP for trivial/boilerplate code.
---

# Robust-solve — diversity as a correctness oracle

A single forward pass writes *almost*-always-correct code, then ships it alone: if it happens to write the
rare buggy variant, nothing catches it. This skill turns the project's measured result
([RESULTS.md](../../RESULTS.md) Benchmarks 5–6: shipped-bug rate cut ~28× from k=1 to k=7) into a workflow.
Mechanism: the bundled [`diff_test.py`](diff_test.py) — it ships inside this skill folder, no repo needed.

## When to run / skip
- **Run** when a subtle bug is costly: non-trivial algorithms, parsers, date/time, money, edge-case-heavy
  logic, or an explicit `/robust-solve`.
- **Skip** for trivial/boilerplate code where the obvious answer is plainly right — say so and just write it.

## Protocol

### 1 · Generate ≥5 STRUCTURALLY DIFFERENT solutions
Not five paraphrases — five genuinely different *approaches* to the same function (e.g. top-down recursion
+ memo, bottom-up DP, iterative/stack, a brute-force-but-obviously-correct version, a mathematically clever
one). The brute-force one is gold: it's the slow oracle the clever ones must agree with. Write each as the
SAME function signature, to separate files (`sol1.py … sol5.py`).

### 2 · Build a fuzz harness
Write a generator that produces hundreds–thousands of **random, edge-biased** inputs for the function
(empty, size 0/1, duplicates, extremes, adversarial structure). No hand-picked happy-path cases — the bug
hides in the inputs you wouldn't think to write.

### 3 · Differential test (the oracle is the disagreement)
Run all solutions on every fuzzed input and compare outputs. Use the bundled tester:
```bash
python diff_test.py    # bundled in this skill folder: runs a self-check, then exposes differential_test(fn_name, [codes...], inputs)
```
Any input where the solutions **disagree** means ≥1 is buggy — found with **no reference solution**. The
brute-force solution breaks ties toward correctness.

### 4 · Investigate every disagreement, then ship the consensus
For each disagreement: figure out which solution is wrong and *why* (this is a real edge-case bug — fix or
discard it). Ship the **majority/consensus** solution (prefer the one that also matches the brute-force
oracle). Re-run the harness until the survivors agree on all fuzzed inputs.

### 5 · Report honestly
- The consensus solution.
- **Bugs caught**: the disagreement inputs and what was wrong (concrete).
- **Residual risk** — the load-bearing honesty: differential testing catches *idiosyncratic* (minority)
  bugs. If **all** your solutions share the same wrong assumption (a systematic misreading of the spec),
  they will agree and be wrong together — **agreement is not proof of correctness.** So also re-read the
  spec adversarially for a shared misconception, especially around the one edge case they all handle the
  same surprising way.

## One-line rationale
A lone solution is confidently alone. Several diverse solutions police each other — and their disagreement
is a free bug detector. Measured: ~28× fewer shipped bugs at k=7 vs k=1 (Benchmark 6).
