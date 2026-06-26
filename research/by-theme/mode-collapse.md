# Mode collapse & creativity loss from alignment/RLHF

*Mode collapse & creativity loss from alignment/RLHF*

[← back to master report](../REPORT.md)

## Key takeaways

- Root cause is two-fold: (1) reverse-KL in PPO/DPO is mode-seeking and sharpens the output distribution, and (2) 'typicality bias' in human preference data — annotators reward familiar text — bakes the collapse in at the DATA level (Verbalized Sampling, 2510.01171). The model still 'knows' many good answers; alignment just stops it from emitting the non-modal ones.
- The generalisation-vs-diversity tradeoff is empirically established (Kirk et al., 2310.06452): the same RLHF step that makes an agent reliable and OOD-robust is what suppresses its diversity. Diversity must therefore be recovered EXTERNALLY at inference — the deployed aligned model won't supply it natively.
- Aligned models fall into 'attractor states' — re-prompting for 'another idea' yields near-duplicates with low entropy and tight embedding clustering (Creativity Has Left the Chat, 2406.05587). Naive resampling is not enough; you must actively repel from prior outputs.
- Swapping or ensembling models does NOT buy diversity — LLMs are creatively homogeneous with each other (Wenger & Kenett, 2501.19361). Diversity has to come from mechanism-level interventions (eliciting the latent distribution, rarity selection, constraint/persona injection), not model variety.
- The most actionable, zero-cost lever is eliciting the model's own latent distribution instead of its argmax: ask for k candidates WITH probabilities and work the low-probability tail (Verbalized Sampling). This is a pure prompting change that recovers 1.6–2.1x diversity.
- The right selection criterion for divergence is 'rare AND high-quality beats common AND high-quality' (DivPO, 2501.18101) — pick the uncommon sound option, not the global quality-argmax. This rule transplants into candidate-ranking without retraining.
- Decoding knobs matter and can be made safe: min-p (2407.01082) and selective/risk-aware sampling (2510.01218) let you raise temperature for exploration while preserving coherence by pruning only truly implausible tokens — crucial for code, where approach should vary but identifiers must not.
- Creativity is multi-dimensional (novelty + surprise + feasibility), not a single 'be creative' instruction (CrPO, 2505.14442). Genuine divergence should be JUDGED on those axes to distinguish real novelty from superficial variation.

## Harness mechanisms

- /diverge skill (Verbalized Sampling): rewrite any ideation prompt to 'Give N approaches to <task>, each with an estimated probability = how conventional it is; then expand the 2 lowest-probability ones that are still sound.' Make this the default front-end to any planning/design phase so the agent starts from the tail of its distribution, not the mode.
- Attractor-breaker resampling loop: keep a running set of already-proposed solutions, inject them as a hard negative constraint ('do not propose anything semantically near: [...]'), and gate each new candidate through an embedding-distance threshold — auto-reject and regenerate if cosine similarity to any prior candidate is too high.
- Rarity-aware candidate critic (DivPO rule): after generating N candidates, score each on (quality, rarity), then SELECT the highest-quality candidate within the rarest tercile rather than the global argmax. Use as the commit step / tie-breaker in design-shotgun and explore flows.
- Per-phase creativity profile (selective sampling + min-p): high temperature with min-p guarding coherence during PLAN/brainstorm phases; greedy/low-temp during IMPLEMENT phases. Only randomize design-decision tokens, keep identifiers and API calls deterministic — fits code agents where approach should diverge but syntax must not.
- Forced-differentiation multi-agent fan-out: because models are creatively homogeneous, give each parallel agent a DISTINCT seed/constraint/persona (different assumed user, forced different core primitive, banned default library) rather than relying on model or sampling variety; add a homogeneity check that re-runs with stronger constraints if outputs converge.
- Novelty-surprise-feasibility LLM-judge (CrPO rubric): score candidates on novelty (unlike common solutions), surprise (violates the obvious expectation), and feasibility; in a generate-critique-revise loop, push toward the surprising-but-correct quadrant and discard merely-varied-but-typical outputs.
- Collapse detector as a harness invariant (Kirk et al.): log a diversity metric (distinct-n / embedding spread) over an agent's open-ended generations; when it drops below threshold, automatically trigger a re-diversify step (verbalized sampling + attractor-breaker) before proceeding.

## Papers

#### 1. [Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity](https://arxiv.org/abs/2510.01171)

- **Authors:** Jiayi Zhang, Simon Yu, Derek Chong, Anthony Sicilia, Michael R. Tomz, Christopher D. Manning, Weiyan Shi  
- **Year / venue:** — · — · arXiv:2510.01171  
- **Verification:** ✅ verified real — via `arxiv id_list (WebFetch)` (arXiv feed title and all 7 authors match exactly.)

- **Method.** Identifies 'typicality bias' in human preference data (annotators favor familiar/conventional text, per cognitive psychology) as a root cause of mode collapse at the DATA level, not just the algorithm. The fix is a training-free prompt: ask the model to verbalize a distribution over k candidate responses WITH explicit probabilities (e.g. 'Generate 5 jokes about coffee and their probabilities'), which recovers the pretrained model's latent diversity that alignment suppressed.
- **Why it matters for divergence.** This is the single most actionable lever for an agent: it shows the collapse is a prompting artifact you can undo at inference time with zero retraining. Instead of accepting the argmax answer, you force the model to surface the tail of its own distribution — exactly the 'non-obvious next move' a divergent coding agent needs. Reports 1.6–2.1x diversity gains while preserving factuality/safety.
- **→ Harness application.** Build a `/diverge` skill that rewrites any ideation/design prompt into a verbalized-sampling form: 'Propose 5 distinct approaches to <task>, each with an estimated probability (your confidence it's the conventional choice). Bias toward the lower-probability ones.' Then the agent explicitly works the low-probability candidates rather than the modal one. Wire this into the planning phase of an agent loop (e.g. before /gsd-plan-phase) so candidate solutions are drawn from the tail, then ranked by a separate quality critic.

#### 2. [Understanding the Effects of RLHF on LLM Generalisation and Diversity](https://arxiv.org/abs/2310.06452)

- **Authors:** Robert Kirk, Ishita Mediratta, Christoforos Nalmpantis, Jelena Luketina, Eric Hambro, Edward Grefenstette, R. Raileanu  
- **Year / venue:** — · — · arXiv:2310.06452  
- **Verification:** ✅ verified real — via `semanticscholar arXiv:2310.06452` (Title and authors match (Raileanu abbreviated in S2). arxiv 429-limited; confirmed via Semantic Scholar.)

- **Method.** Systematic comparison of base, SFT, and RLHF models on out-of-distribution generalisation vs per-input output diversity. Finds RLHF improves OOD generalisation but SIGNIFICANTLY reduces output diversity vs SFT across multiple diversity metrics — establishing a fundamental generalisation-vs-diversity tradeoff in current fine-tuning.
- **Why it matters for divergence.** Foundational diagnosis: it is the canonical empirical evidence that the very training step that makes an aligned agent reliable is what kills its diversity. Tells the harness designer that diversity must be RECOVERED externally (prompting/decoding/sampling) because the deployed aligned model will not supply it natively, and that you should not expect a single sample to represent the model's range.
- **→ Harness application.** Encode the tradeoff as a harness invariant: never trust a single generation for any open-ended subtask. Make the agent loop sample N candidates by default for ideation/design/naming/test-case-generation steps, and reserve low-temperature single-shot only for deterministic mechanical edits. Add a diversity metric (distinct-n / embedding spread) as a logged signal so the agent can detect when it has collapsed and auto-trigger a re-diversify step.

#### 3. [Creativity Has Left the Chat: The Price of Debiasing Language Models](https://arxiv.org/abs/2406.05587)

- **Authors:** Behnam Mohammadi  
- **Year / venue:** — · — · arXiv:2406.05587  
- **Verification:** ✅ verified real — via `semanticscholar arXiv:2406.05587` (Title and single author match exactly.)

- **Method.** Three experiments on the Llama-2 series show aligned/debiased models exhibit lower token-prediction entropy, cluster tightly in embedding space, and gravitate toward 'attractor states' — a limited set of repeated outputs — relative to base models. Quantifies the creativity cost of RLHF debiasing.
- **Why it matters for divergence.** Names and demonstrates the 'attractor state' failure mode: an aligned model repeatedly falls back to the same few outputs across independent calls. For an agent, this explains why re-prompting for 'another idea' yields near-duplicates. Motivates explicit anti-attractor mechanisms (banning prior outputs, forcing semantic distance) rather than naive resampling.
- **→ Harness application.** Add an 'attractor-breaker' to multi-sample loops: maintain a running set of already-proposed solutions and inject them into the prompt as a negative constraint ('Do NOT propose anything semantically close to: [list]'). Combine with an embedding-distance gate that rejects a new candidate if cosine similarity to any prior candidate exceeds a threshold, forcing the agent off the attractor.

#### 4. [Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs](https://arxiv.org/abs/2407.01082)

- **Authors:** Minh Nhat Nguyen, Andrew Baker, Clement Neo, Allen Roush, Andreas Kirsch, Ravid Shwartz-Ziv  
- **Year / venue:** — · — · arXiv:2407.01082  
- **Verification:** ✅ verified real — via `arxiv id_list (WebFetch)` (arXiv feed title and all 6 authors match exactly.)

- **Method.** A dynamic truncation decoding method that sets the token cutoff relative to the top token's probability (threshold scales with model confidence), instead of nucleus sampling's fixed mass. This lets you push temperature high for diversity without the incoherence/repetition that fixed top-p produces. Adopted in HuggingFace Transformers and vLLM.
- **Why it matters for divergence.** Gives a knob to widen the candidate set safely: high temperature normally trades quality for diversity, but min-p preserves coherence at high temp by adaptively pruning the truly implausible tokens. The mechanism that lets an agent explore the tail of its distribution without producing garbage.
- **→ Harness application.** When the harness controls sampling params (local models / API with min_p), set min_p (~0.05–0.1) plus elevated temperature (~1.5) specifically for divergent-generation subtasks, and switch back to greedy/low-temp for execution. Expose this as a per-phase 'creativity profile' in the agent config so the loop raises temperature with min-p guarding coherence during brainstorm phases and lowers it during code-edit phases.

#### 5. [Diverse Preference Optimization](https://arxiv.org/abs/2501.18101)

- **Authors:** Jack Lanchantin, Angelica Chen, S. Dhuliawala, Ping Yu, J. Weston, Sainbayar Sukhbaatar, Ilia Kulikov  
- **Year / venue:** — · — · arXiv:2501.18101  
- **Verification:** ✅ verified real — via `semanticscholar arXiv:2501.18101` (Title and all 7 authors match (some initials abbreviated in S2).)

- **Method.** A preference-optimization variant where, from a pool of sampled responses, the CHOSEN example is rare-but-high-quality and the REJECTED example is common-but-low-quality (diversity measured over the pool). This directly counteracts the distribution-sharpening of standard DPO/RLHF. Yields 45.6% more diverse persona attributes and 74.6% more story diversity at similar win rates.
- **Why it matters for divergence.** Reframes the selection criterion that matters for divergence: pick the RARE high-quality option, penalize the COMMON one. Even without retraining, this 'rare-and-good beats common-and-good' rule is a directly transplantable ranking heuristic for an agent choosing among its own candidate outputs.
- **→ Harness application.** Implement DivPO's selection rule as a candidate-ranking critic in the agent loop: after generating N solutions, score each on (quality, rarity) and select the highest-quality candidate among the rarest tercile rather than the global-quality argmax. Use this as the tie-breaker in /gsd-explore or design-shotgun style flows so the agent systematically commits to the uncommon-but-sound option instead of the safe modal one.

#### 6. [Creative Preference Optimization](https://arxiv.org/abs/2505.14442)

- **Authors:** Mete Ismayilzada, Antonio Laverghetta, Simone A. Luchini, Reet Patel, Antoine Bosselut, Lonneke van der Plas, Roger E. Beaty  
- **Year / venue:** — · — · arXiv:2505.14442  
- **Verification:** ✅ verified real — via `semanticscholar arXiv:2505.14442` (Title and all 7 authors match (Laverghetta Jr. and Beaty's initial variant in S2).)

- **Method.** CrPO injects signals from 30+ psychological creativity dimensions (novelty, surprise, diversity, etc.) modularly into the preference-optimization objective, trained on MuCE (200k+ human responses scored on validated creativity assessments). Resulting models beat GPT-4o on automated and human evals for novel/diverse/surprising generations at maintained quality; validated on NoveltyBench.
- **Why it matters for divergence.** Operationalizes creativity as a multi-dimensional rubric (novelty, surprise, diversity) rather than a single 'be creative' instruction. An agent can borrow these dimensions as explicit evaluation axes to judge whether a candidate is genuinely divergent or merely superficially varied.
- **→ Harness application.** Turn the creativity dimensions into an LLM-judge rubric the harness applies to candidate solutions: score each on novelty (unlike known/common solutions), surprise (violates the obvious expectation), and feasibility, then keep candidates that are high-novelty AND high-feasibility. Use this rubric as the reward signal in a generate-critique-revise loop so the agent iteratively pushes outputs toward the surprising-but-correct quadrant.

#### 7. [We're Different, We're the Same: Creative Homogeneity Across LLMs](https://arxiv.org/abs/2501.19361)

- **Authors:** Emily Wenger, Yoed N. Kenett  
- **Year / venue:** — · — · arXiv:2501.19361  
- **Verification:** ✅ verified real — via `semanticscholar arXiv:2501.19361` (Title and both authors match exactly.)

- **Method.** Using standardized human creativity tests (e.g. divergent association / alternate-uses style tasks), shows LLM creative responses are far more similar to OTHER LLMs' responses than humans are to each other, even after controlling for response structure — i.e. cross-model creative homogenization, not just within-model collapse.
- **Why it matters for divergence.** Warns that simply swapping models (or ensembling several aligned models) does NOT buy diversity — they share the same attractors. For a harness this means inter-model ensembling is a weak diversity source; you need mechanism-level interventions (verbalized sampling, rarity selection, persona/constraint injection) instead.
- **→ Harness application.** Do not rely on multi-model voting/ensembles to generate diverse ideas (they converge). Instead, in any multi-agent design-shotgun flow, give each agent a DISTINCT structural constraint or persona/seed (different assumed user, different architectural style, forced different primitive) to manufacture diversity that cross-model sampling won't provide. Add a homogeneity check that flags when parallel agents produced near-identical outputs and re-runs with stronger differentiating constraints.

#### 8. [Control the Temperature: Selective Sampling for Diverse and High-Quality LLM Outputs](https://arxiv.org/abs/2510.01218)

- **Authors:** S. Troshin, Wafaa Mohammed, Yan Meng, C. Monz, Antske Fokkens, Vlad Niculae  
- **Year / venue:** — · — · arXiv:2510.01218  
- **Verification:** ✅ verified real — via `semanticscholar arXiv:2510.01218` (Title matches exactly. The original candidate listed authors as 'Anonymous / arXiv preprint authors'; real authors are Troshin, Mohammed, Meng, Monz, Fokkens, Niculae. Paper is real and id is correct.)

- **Method.** Per-token selective sampling: computes a 'sampling risk' metric at each decoding step and dynamically switches between greedy decoding (low-risk, quality-critical tokens) and high-temperature sampling (low-risk-to-creativity tokens), improving the quality-diversity Pareto frontier even at high global temperature.
- **Why it matters for divergence.** Refines the diversity knob to be token-aware: it injects randomness only where it won't break correctness, so an agent can be exploratory in 'idea' tokens and deterministic in 'syntax/fact' tokens. Directly relevant to code generation, where you want divergent approach-choices but exact, non-random API names.
- **→ Harness application.** For code agents, approximate selective sampling at the structural level: run divergent high-temp sampling for the PLAN/approach (where exploration helps) and deterministic low-temp for the IMPLEMENTATION (where correctness dominates). Where the harness has token-level control, gate temperature on a risk signal so the agent only randomizes design-decision tokens, keeping identifiers and call signatures deterministic.
