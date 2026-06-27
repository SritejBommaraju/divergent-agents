# Benchmark scoreboard

Every benchmark in this project, what it measured, the **honest** finding (wins *and* nulls), and the
command to reproduce it. Methodology and its traps: [`../BENCHMARKING.md`](../BENCHMARKING.md) (23 verified
papers). Full write-ups with CIs and caveats: [`../RESULTS.md`](../RESULTS.md).

| # | Benchmark | Measures | Honest finding | Reproduce |
|---|---|---|---|---|
| **1** | DAT (Divergent Association Task) | objective semantic diversity, no judge | **Prompting "be divergent" is a NULL** (within-response 99.7 vs 99.6, p=0.84). The structural **archive lifts population diversity +0.229, p<0.0001**, no quality loss. | `python bench/run_dat.py` |
| **2** | Coding solution diversity | distinct correct algorithms / 10 | best-of-N collapses to **1.33** distinct algos; engine lenses give **9.33** (**7×**), 30/30 still correct. | `python bench/run_code.py` |
| **3** | Cognitive routing | accuracy + router differentiation | Accuracy is a **100% ceiling** (no strategy effect). Router picks **9/10 distinct mode-plans** — breadth/adaptivity, not accuracy. | `python bench/run_reasoning.py bench/data/reasoning_hard_raw.json reasoning_tasks_hard` |
| **4** | Proper pass@k (novel problems) | unbiased pass@k, compute-matched, non-oracle select | Near-perfect ceiling: baseline 0.972 / engine 1.000, **both 1.0 by k=2** — no coverage advantage. The methodologically-correct negative. | `python bench/run_code_hard.py bench/data/code_twist_raw.json code_twist` |
| **5** | Fuzz + differential testing | hidden bugs under 2000 adversarial inputs | The fixed-test ceiling was optimistic: **2/72 solutions fail fuzzing**. Diversity = correctness oracle: **383 disagreements, majority correct 383/383**. | `python bench/fuzz_eval.py bench/data/code_twist_raw.json 2000` |
| **6** | Robustness vs k (rigorous) | shipped-bug rate as a function of k | **Shipped-error rate falls ~28×** (k=1→k=7). 657/657 bug-exposing inputs idiosyncratic → majority vote fixes them. 0 systematic (this set). | `python bench/robustness.py 600` |
| **L** | Closed-loop learning | does routing learn from external signal? | Trained on the real diversity signal, learns `maximize_diversity→archive`; **generalizes out-of-sample (+0.232)**. | `python engine/close_loop.py` |

## The one-paragraph synthesis

A frontier model at low effort is at the **pass@k ceiling on anything you can construct-and-check** (B3,
B4) — so "more kinds of thinking" does **not** raise accuracy on solvable problems, and we never pretend it
does. Its measured value is elsewhere and real: structure escapes **mode collapse** (B1 archive, generalized
by the closed loop), the engine **covers the solution space** far better than best-of-N (B2), the router
**deploys the right mode per problem** (B3), and — the strongest correctness result — **diverse solutions
police each other**, cutting shipped bugs ~28× via differential testing (B5–B6). The honest limit throughout:
differential testing catches *idiosyncratic* bugs, not *systematic* ones; agreement is not proof of
correctness; and a genuine accuracy win awaits a non-saturated, checkable task distribution (or a
cross-family judge) we did not have.

## Integrity notes (how we kept ourselves honest)

- **Every cited paper verified twice** (arXiv API + Semantic Scholar/Crossref): 78 + 23 + 36 papers,
  0 fabrications. See [`../research/verification.md`](../research/verification.md).
- **Generation and scoring are always separate** — the model that writes answers never grades them.
  Objective metrics (embeddings, brute-validated checkers) carry every headline; **no LLM-judge claims**
  (we lack a cross-family judge).
- **Checkers are validated** (gold passes, wrong fails; brute references cross-checked against independent
  enumerations on 350+ cases).
- **Nulls and artifacts reported, not buried** — the prompting null (B1), the accuracy ceiling (B3, B4), and
  a grading artifact we caught and fixed (B3) are all documented.
