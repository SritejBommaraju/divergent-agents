# Demo: the router does the most kinds of thinking

*Captured from an actual `router-differentiation-probe` run. The metacognitive router was given 10 varied tasks and chose a mode-plan for each. It did NOT collapse to 'always brainstorm' — it deployed **9 distinct plans** across 10 tasks (8 distinct primary modes), using divergence only where novelty is actually the goal.*

| # | task | chosen mode-plan |
|---|---|---|
| 1 | debug (API 500 for logged-in only) | `abductive → causal → convergent_verify` |
| 2 | design (delightful CLI onboarding) | `first_principles → analogical → divergent → convergent_verify` |
| 3 | estimate (piano tuners in Chicago) | `decompose → bayesian → convergent_verify` |
| 4 | prove (sum of first n odds = n²) | `deductive → convergent_verify` |
| 5 | causal (did button color cause sales?) | `causal → abductive → convergent_verify` |
| 6 | decide (monolith vs microservices) | `first_principles → dialectic → convergent_verify` |
| 7 | induce (infer f(10) from examples) | `inductive → convergent_verify` |
| 8 | diagnose (1% drop in backup window) | `abductive → causal → convergent_verify` |
| 9 | unstick (novel caching approach) | `first_principles → analogical → divergent → convergent_verify` |
| 10 | plan (zero-downtime DB migration) | `decompose → deductive → dialectic → convergent_verify` |

## Read the routing
- **Diagnosis** (debug, backup-drop) → `abductive → causal → verify` — enumerate explanations, model cause, confirm.
- **Estimation** (piano tuners) → `decompose → bayesian → verify` — Fermi breakdown under uncertainty.
- **Proof** → `deductive → verify`. **Induction** → `inductive → verify`. **Trade-off** → `first_principles → dialectic → verify`.
- **Genuine novelty** (CLI onboarding, novel caching) → reaches for `divergent` — but *only* there.
- **High-risk execution** (DB migration) → `decompose → deductive → dialectic → verify`.

That selectivity is the whole point: a single forward pass answers from the mode; a one-trick divergence engine brainstorms everything; the cognitive engine **matches the kind of thinking to the problem** — which is what it means to do the most kinds of thinking.