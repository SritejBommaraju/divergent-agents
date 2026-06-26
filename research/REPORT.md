# Master Report — Turning Coding Agents from Predictors into Divergent Thinkers

> A verified survey of every method we found for pushing a general-purpose coding agent (Claude Code, Codex) past the single most-likely answer into genuine novelty — and how each one maps onto a concrete harness/skill mechanism.

## At a glance

- **Themes researched:** 10
- **Papers found:** 78
- **Independently confirmed real:** 78 / 78
- **Unresolved / flagged:** 0
- **Real but not on arXiv (verified via publisher/Semantic Scholar):** 3

**How verification works.** Each paper was found by a per-theme research scout, then re-checked by a separate strict verifier that re-fetched it from the arXiv API (`export.arxiv.org/api/query?id_list=…`) or Semantic Scholar and confirmed the returned title/authors match. A paper is marked ✅ only if a matching record was actually retrieved. See [`verification.md`](verification.md) for the independent re-check ledger.

## Themes

1. [Mode collapse & creativity loss from alignment/RLHF](#1-mode-collapse) — 8 papers
2. [Sampling & decoding strategies for diversity/novelty](#2-decoding-sampling) — 8 papers
3. [Quality-Diversity, Novelty Search & open-endedness](#3-quality-diversity) — 8 papers
4. [LLM-driven evolution & program/idea search](#4-llm-evolution) — 8 papers
5. [Structured reasoning & search at inference time](#5-inference-search) — 8 papers
6. [Self-reflection, critique & multi-agent debate](#6-reflection-debate) — 8 papers
7. [Research-idea generation & autonomous scientific discovery](#7-idea-generation) — 8 papers
8. [Analogical, lateral & conceptual-blending reasoning](#8-analogy-lateral) — 8 papers
9. [Measuring creativity, novelty, surprise & diversity in LLM output](#9-creativity-eval) — 7 papers
10. [Exploration, curiosity & intrinsic motivation for reasoning agents](#10-rl-exploration) — 7 papers


---

## 1. Mode collapse & creativity loss from alignment/RLHF

<a id='1-mode-collapse'></a>

*Mode collapse & creativity loss from alignment/RLHF*

**Key takeaways**

- Root cause is two-fold: (1) reverse-KL in PPO/DPO is mode-seeking and sharpens the output distribution, and (2) 'typicality bias' in human preference data — annotators reward familiar text — bakes the collapse in at the DATA level (Verbalized Sampling, 2510.01171). The model still 'knows' many good answers; alignment just stops it from emitting the non-modal ones.
- The generalisation-vs-diversity tradeoff is empirically established (Kirk et al., 2310.06452): the same RLHF step that makes an agent reliable and OOD-robust is what suppresses its diversity. Diversity must therefore be recovered EXTERNALLY at inference — the deployed aligned model won't supply it natively.
- Aligned models fall into 'attractor states' — re-prompting for 'another idea' yields near-duplicates with low entropy and tight embedding clustering (Creativity Has Left the Chat, 2406.05587). Naive resampling is not enough; you must actively repel from prior outputs.
- Swapping or ensembling models does NOT buy diversity — LLMs are creatively homogeneous with each other (Wenger & Kenett, 2501.19361). Diversity has to come from mechanism-level interventions (eliciting the latent distribution, rarity selection, constraint/persona injection), not model variety.
- The most actionable, zero-cost lever is eliciting the model's own latent distribution instead of its argmax: ask for k candidates WITH probabilities and work the low-probability tail (Verbalized Sampling). This is a pure prompting change that recovers 1.6–2.1x diversity.
- The right selection criterion for divergence is 'rare AND high-quality beats common AND high-quality' (DivPO, 2501.18101) — pick the uncommon sound option, not the global quality-argmax. This rule transplants into candidate-ranking without retraining.
- Decoding knobs matter and can be made safe: min-p (2407.01082) and selective/risk-aware sampling (2510.01218) let you raise temperature for exploration while preserving coherence by pruning only truly implausible tokens — crucial for code, where approach should vary but identifiers must not.
- Creativity is multi-dimensional (novelty + surprise + feasibility), not a single 'be creative' instruction (CrPO, 2505.14442). Genuine divergence should be JUDGED on those axes to distinguish real novelty from superficial variation.

**Harness mechanisms this theme suggests**

- /diverge skill (Verbalized Sampling): rewrite any ideation prompt to 'Give N approaches to <task>, each with an estimated probability = how conventional it is; then expand the 2 lowest-probability ones that are still sound.' Make this the default front-end to any planning/design phase so the agent starts from the tail of its distribution, not the mode.
- Attractor-breaker resampling loop: keep a running set of already-proposed solutions, inject them as a hard negative constraint ('do not propose anything semantically near: [...]'), and gate each new candidate through an embedding-distance threshold — auto-reject and regenerate if cosine similarity to any prior candidate is too high.
- Rarity-aware candidate critic (DivPO rule): after generating N candidates, score each on (quality, rarity), then SELECT the highest-quality candidate within the rarest tercile rather than the global argmax. Use as the commit step / tie-breaker in design-shotgun and explore flows.
- Per-phase creativity profile (selective sampling + min-p): high temperature with min-p guarding coherence during PLAN/brainstorm phases; greedy/low-temp during IMPLEMENT phases. Only randomize design-decision tokens, keep identifiers and API calls deterministic — fits code agents where approach should diverge but syntax must not.
- Forced-differentiation multi-agent fan-out: because models are creatively homogeneous, give each parallel agent a DISTINCT seed/constraint/persona (different assumed user, forced different core primitive, banned default library) rather than relying on model or sampling variety; add a homogeneity check that re-runs with stronger constraints if outputs converge.
- Novelty-surprise-feasibility LLM-judge (CrPO rubric): score candidates on novelty (unlike common solutions), surprise (violates the obvious expectation), and feasibility; in a generate-critique-revise loop, push toward the surprising-but-correct quadrant and discard merely-varied-but-typical outputs.
- Collapse detector as a harness invariant (Kirk et al.): log a diversity metric (distinct-n / embedding spread) over an agent's open-ended generations; when it drops below threshold, automatically trigger a re-diversify step (verbalized sampling + attractor-breaker) before proceeding.

### Papers

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


---

## 2. Sampling & decoding strategies for diversity/novelty

<a id='2-decoding-sampling'></a>

*Sampling & decoding strategies for diversity/novelty*

**Key takeaways**

- The single most-likely continuation (greedy/argmax) is a known failure mode: it degenerates into bland repetition. Genuine novelty lives in a middle band, off argmax but inside a coherence boundary.
- Static thresholds (fixed top-k/top-p/temperature) are suboptimal because the safe distance off argmax depends on local uncertainty. The strongest methods (eta-sampling, min-p, locally-typical) make truncation adaptive to the model's per-step entropy/confidence.
- Contrastive methods (contrastive decoding, DoLa) show novelty can be steered by subtraction: explicitly suppress the generic/obvious/premature baseline (an 'amateur' model or an early layer) to surface distinctive, higher-information content.
- Diversity can be enforced structurally, not just stochastically: Diverse Beam Search adds an explicit inter-candidate dissimilarity penalty so options span the space rather than cluster on paraphrases of the top answer.
- Mode collapse is partly an alignment artifact (typicality bias in preference data), and Verbalized Sampling shows it can be undone at the prompt level alone, no decoding-knob access required, which is critical for closed agents like Claude/GPT.
- There is a consistent quality/diversity trade-off, but the frontier paper (min-p) shows you can push temperature far higher than default if truncation is confidence-scaled, decoupling 'creative' from 'incoherent.'
- Two complementary intervention layers exist for an agent: the decoding layer (temperature, min_p, typical_p, top_p when the API exposes them) and the prompt/loop layer (verbalized distributions, diverse-candidate penalties, contrast-against-baseline) which works even with no logit access.

**Harness mechanisms this theme suggests**

- Two-pass exploration profile: an 'ideation pass' run hot (high temperature + min_p, or verbalized sampling) that emits several materially distinct solution sketches, followed by a near-greedy 'commit pass' that locks in one and writes correct code. Different decoding settings per phase of the same task.
- Verbalized-distribution ideation skill: replace every 'propose an approach' with 'propose N distinct approaches with confidence weights, including at least one deliberate long-shot,' then force the agent to seriously evaluate a non-top option. Directly ports Verbalized Sampling into a Claude Code skill, no API knobs needed.
- Contrast-against-the-obvious loop: first elicit the cliche baseline answer (cheap model or a 'lazy/generic' persona of the same model), then instruct the main agent to produce a solution that measurably diverges from that baseline, using the baseline as an explicit negative-exemplar list. Prompt-level contrastive decoding.
- Diverse-candidate penalty: when generating option k, feed it the key design choices of options 1..k-1 with an instruction to maximize dissimilarity (different library/algorithm/architecture). Reproduces Diverse Beam Search's inter-group penalty so the agent's option set spans the space instead of paraphrasing the argmax.
- Uncertainty-aware divergence controller: at decision points, inspect the model's entropy/logprobs (where available) and widen the search (more samples, higher temp) only at high-entropy junctures (genuine design forks) while staying tight at low-entropy mechanical steps. Implements eta-sampling's adaptive-truncation idea at the agent-loop level.
- Fast-vs-deliberate self-contrast (DoLa analog): capture the snap first-draft answer, run a deeper deliberation pass, and prefer conclusions that survive deeper analysis over the premature one, filtering cheap defaults while keeping grounded novelty.
- Decoding-knob presets exposed as named modes: 'brainstorm' (temp 1.3-1.5 + min_p 0.05 / typical_p), 'balanced', 'precise' (temp 0.2, near-greedy), so the harness can switch the model's divergence level explicitly per subtask rather than relying on one global temperature.

### Papers

#### 1. [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751)

- **Authors:** Ari Holtzman, Jan Buys, Li Du, Maxwell Forbes, Yejin Choi  
- **Year / venue:** — · — · arXiv:1904.09751  
- **Verification:** ✅ verified real — via `arxiv id_list 1904.09751` (Title and authors match exactly.)

- **Method.** Introduces nucleus (top-p) sampling: at each step truncate to the smallest set of tokens whose cumulative probability exceeds p, then renormalize and sample. Diagnoses that maximizing likelihood (greedy/beam) yields bland, repetitive text and that the distribution's unreliable low-probability tail must be cut, not sampled flat.
- **Why it matters for divergence.** The foundational argument that the single most-likely continuation is a trap: pure argmax decoding degenerates into repetition, while uncapped sampling drifts into incoherence. Nucleus sampling is the canonical knob for moving mass off argmax into a coherent-but-varied band, establishing the quality/diversity trade-off every later method tunes.
- **→ Harness application.** Expose a per-task 'exploration profile' in the agent loop: when generating candidate designs/approaches (not final code), raise top-p (e.g. 0.95) and temperature; when emitting syntax-critical tokens, drop to near-greedy. A skill could split a task into a high-p 'ideation pass' that samples several distinct solution sketches, then a low-p 'commit pass' that locks in one.

#### 2. [Diverse Beam Search: Decoding Diverse Solutions from Neural Sequence Models](https://arxiv.org/abs/1610.02424)

- **Authors:** Ashwin K Vijayakumar, Michael Cogswell, Ramprasath R. Selvaraju, Qing Sun, Stefan Lee, David Crandall, Dhruv Batra  
- **Year / venue:** — · — · arXiv:1610.02424  
- **Verification:** ✅ verified real — via `arxiv id_list 1610.02424` (Title and authors match exactly.)

- **Method.** Partitions the beam into groups and adds a dissimilarity penalty between groups so that each group's hypotheses are explicitly pushed away from tokens already chosen by other groups, yielding a list of diverse decodings instead of near-identical beam variants.
- **Why it matters for divergence.** Directly attacks the failure mode where the top-B continuations are trivial paraphrases of the argmax. The diversity penalty is a mechanism for forcing genuinely different branches, the structural analog of asking an agent for several materially distinct plans rather than one answer plus restatements.
- **→ Harness application.** Encode a 'diverse plan' loop: generate N candidate solutions, but feed each new generation a running list of the prior candidates' key choices (library, algorithm, file layout) with an instruction to maximize dissimilarity from them. This reproduces the inter-group penalty at the prompt level, guaranteeing the agent's option set spans the space instead of clustering on the obvious answer.

#### 3. [Locally Typical Sampling](https://arxiv.org/abs/2202.00666)

- **Authors:** Clara Meister, Tiago Pimentel, Gian Wiher, Ryan Cotterell  
- **Year / venue:** — · — · arXiv:2202.00666  
- **Verification:** ✅ verified real — via `arxiv id_list 2202.00666` (Title and authors match exactly.)

- **Method.** Grounded in information theory, selects tokens whose negative log-probability (surprisal) is close to the conditional entropy of the model at that step, i.e. tokens that are 'typically informative' rather than simply highest-probability, sampling from that locally-typical set.
- **Why it matters for divergence.** Reframes good generation as matching a human-like information rate, not maximizing probability. This is a principled way to deliberately admit moderately-surprising tokens (novelty) while excluding both the safe argmax and the incoherent tail, exactly the 'novel-but-coherent' band an agent needs.
- **→ Harness application.** When the inference API exposes typical_p (HF/vLLM do), surface it as a knob the agent raises during brainstorming. Conceptually, a skill can implement an 'information-rate filter': reject candidate ideas that are too obvious (near-zero surprisal, generic boilerplate) AND too incoherent (off-topic), keeping the middle band, an entropy-matched novelty gate over self-generated options.

#### 4. [Truncation Sampling as Language Model Desmoothing](https://arxiv.org/abs/2210.15191)

- **Authors:** John Hewitt, Christopher D. Manning, Percy Liang  
- **Year / venue:** — · — · arXiv:2210.15191  
- **Verification:** ✅ verified real — via `arxiv id_list 2210.15191` (Title and authors match exactly.)

- **Method.** Casts an LM as a mixture of the true distribution plus a smoothing distribution; truncation should 'desmooth' by recovering the true support. Introduces eta-sampling, an entropy-dependent probability threshold that truncates more aggressively when the model is confident and less when it is uncertain.
- **Why it matters for divergence.** Provides the theory for why a fixed top-p/top-k threshold is wrong: how far off argmax you can safely wander depends on the model's local uncertainty. Adaptive truncation lets an agent be bold (wide net) exactly where many continuations are plausible and conservative where one answer is clearly correct.
- **→ Harness application.** Build an uncertainty-aware exploration controller: read the model's entropy/logprobs at decision points and widen the candidate net (more samples, higher temp) only at high-entropy junctures (design choices), staying tight at low-entropy ones (mechanical edits). This auto-tunes 'how divergent to be' per step instead of using one global temperature.

#### 5. [Contrastive Decoding: Open-ended Text Generation as Optimization](https://arxiv.org/abs/2210.15097)

- **Authors:** Xiang Lisa Li, Ari Holtzman, Daniel Fried, Percy Liang, Jason Eisner, Tatsunori Hashimoto, Luke Zettlemoyer, Mike Lewis  
- **Year / venue:** — · — · arXiv:2210.15097  
- **Verification:** ✅ verified real — via `arxiv id_list 2210.15097` (Title and authors match exactly.)

- **Method.** Scores continuations by the log-probability difference between a strong 'expert' LM and a weak 'amateur' LM (subject to a plausibility constraint), preferring tokens the expert favors much more than the amateur, which suppresses generic, repetitive, low-information modes.
- **Why it matters for divergence.** A concrete mechanism for subtracting the 'obvious' baseline: the amateur encodes exactly the cliched, high-frequency continuations, and contrasting them away pushes generation toward content distinctive to the capable model. This is the decoding-level version of 'don't just say the predictable thing.'
- **→ Harness application.** Implement contrast at the agent level: prompt a small/cheap model (or the same model with a 'generic, lazy' persona) for the obvious answer, then instruct the main agent to explicitly produce a solution that diverges from that baseline. Use the cheap model's output as a negative exemplar list ('avoid these predictable approaches') to steer the strong model off the cliche.

#### 6. [DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models](https://arxiv.org/abs/2309.03883)

- **Authors:** Yung-Sung Chuang, Yujia Xie, Hongyin Luo, Yoon Kim, James Glass, Pengcheng He  
- **Year / venue:** — · — · arXiv:2309.03883  
- **Verification:** ✅ verified real — via `arxiv id_list 2309.03883` (Title and authors match exactly.)

- **Method.** Contrasts the next-token logits from a later transformer layer against those from an earlier layer, amplifying the information that 'matures' in deeper layers (where factual knowledge concentrates) and down-weighting premature, surface-level predictions, with no extra training.
- **Why it matters for divergence.** Shows that contrastive signals internal to one model can push the output distribution away from shallow defaults toward higher-information tokens. For divergence, it is a proof-of-concept that the 'obvious' early-layer prediction can be programmatically suppressed in favor of more considered continuations, improving coherence/factuality of novel outputs.
- **→ Harness application.** Analogize the early-vs-late contrast as a fast-vs-deliberate agent contrast: capture the model's immediate first-draft answer, then run an explicit deeper deliberation pass and instruct it to prefer conclusions that survive the deeper analysis over the snap answer. Useful as a self-critique stage that filters cheap, premature solutions while keeping novel ones grounded.

#### 7. [Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs](https://arxiv.org/abs/2407.01082)

- **Authors:** Minh Nhat Nguyen, Andrew Baker, Clement Neo, Allen Roush, Andreas Kirsch, Ravid Shwartz-Ziv  
- **Year / venue:** — · — · arXiv:2407.01082  
- **Verification:** ✅ verified real — via `arxiv id_list 2407.01082` (Title matches exactly; arxiv lists first author as 'Minh Nhat Nguyen' (candidate gave 'Minh Nguyen').)

- **Method.** Dynamic truncation that sets the cutoff as a fraction (p_base) of the top token's probability, so the admitted set scales with model confidence: wide when the model is uncertain, narrow when confident. This keeps outputs coherent even at high temperature.
- **Why it matters for divergence.** Directly solves the central tension of this theme, how to crank temperature for creativity without falling into incoherence. Min-p lets an agent run hot (genuine novelty) while the confidence-scaled floor prevents nonsense, demonstrated to improve both quality and diversity up to large temperatures.
- **→ Harness application.** If the serving stack exposes min_p (vLLM, llama.cpp, HF, many APIs do), set it as the default truncation method for ideation tasks and pair it with high temperature, giving the agent a 'creative mode' that is safe to turn up. Provide a skill preset: temperature 1.5 + min_p 0.05 for divergent brainstorming, temperature 0.2 for final code emission.

#### 8. [Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity](https://arxiv.org/abs/2510.01171)

- **Authors:** Jiayi Zhang, Simon Yu, Derek Chong, Anthony Sicilia, Michael R. Tomz, Christopher D. Manning, Weiyan Shi  
- **Year / venue:** — · — · arXiv:2510.01171  
- **Verification:** ✅ verified real — via `arxiv id_list 2510.01171` (Title matches exactly; candidate authors listed as 'Jiayi Zhang et al. (CHATS-lab)' — arxiv full author list confirmed.)

- **Method.** A training-free prompting strategy: instead of asking for one answer, ask the model to verbalize a set of candidate responses together with their probabilities ('give 5 X and their likelihoods'), then sample from that verbalized distribution. Attributes alignment-induced mode collapse to a typicality bias in preference data.
- **Why it matters for divergence.** The most directly agent-applicable result here: it recovers diversity (2-3x) purely through prompting, no decoding-API access needed, by making the model surface its own distribution rather than collapsing to the single aligned-safe mode. This is the prompt-level lever for divergence that works on Claude/GPT/Gemini today.
- **→ Harness application.** Bake the verbalized-distribution pattern into an ideation skill: replace 'propose an approach' with 'propose 5 materially different approaches with your estimated probability/confidence for each, including at least one low-probability long-shot,' then have the agent pursue a deliberately non-top option to escape the safe default. Also use it for synthetic test-case and edge-case generation where coverage beats the single likeliest case.


---

## 3. Quality-Diversity, Novelty Search & open-endedness

<a id='3-quality-diversity'></a>

*Quality-Diversity, Novelty Search & open-endedness*

**Key takeaways**

- Objectives are deceptive: directly maximizing the target metric reliably traps search in local optima; rewarding behavioral NOVELTY (distance from an archive of past behaviors) discovers the stepping stones that actually reach hard goals (Novelty Search). This is the core license for an agent to not always pick the modal next token/move.
- Keep an ARCHIVE, not a single best. MAP-Elites' central move — bin solutions by human-chosen behavior dimensions and keep the best per bin — turns 'find the answer' into 'illuminate the space of qualitatively different good answers,' guaranteeing coverage and breaking mode collapse.
- Pure novelty is necessary but not sufficient: most novel things are trivial. A foundation model can supply human-aligned TASTE (OMNI's 'model of interestingness') to steer divergence toward novelty that is both feasible and worthwhile — the crucial filter between mode-collapse and useless wandering.
- LLMs are far more valuable as DIVERSITY ENGINES inside a QD loop than as one-shot answerers: ELM uses the LLM as an intelligent mutation operator, QDAIF uses it as both variation generator and natural-language quality/diversity judge, FunSearch uses it to mutate programs across an island archive. The pattern is: LLM proposes variation, an archive enforces diversity, an evaluator enforces quality.
- AI feedback unlocks QD for fuzzy domains. You don't need a numeric fitness function — you can ask the model in plain language 'how good is this?' and 'how different is this from these others?' (QDAIF/QDHF), making novelty search usable for writing, design, and research ideation where no metric exists.
- Stepping-stones come from cross-pollination and self-generated curricula: POET transfers solutions between sibling problems; OMNI-EPIC and POET invent their own increasingly diverse, learnable-yet-interesting problems and retain BOTH successes and informative failures in the archive.
- Exploration beats greedy trajectories on hard tasks: Intelligent Go-Explore keeps an archive of reached states and uses model taste to decide where to RETURN and branch from, beating Reflexion-style single-trajectory agents exactly where forward-only reasoning gets stuck.
- The whole lineage now reaches coding agents directly (ELM, FunSearch, OMNI-EPIC, Darwin Godel Machine), so 'archive + novelty + interestingness gate + LLM mutation' is a concrete, proven blueprint for a divergent coding harness, not just an RL/robotics idea.

**Harness mechanisms this theme suggests**

- Behavior-characterization + novelty archive: after generating each candidate solution, have the agent emit a compact behavior descriptor (approach-tags or an embedding), store it, and score new candidates by k-NN distance to the archive. Select the most-novel-yet-viable candidate instead of the modal one. A '/diverge' skill could force N candidates, embed, and rank by novelty.
- MAP-Elites grid skill: ask for (or infer) 2-3 axes of variation for the task (e.g. paradigm x dependency-footprint x complexity for code; tone x structure x length for writing), maintain a literal grid file, bin each generated candidate, keep only per-cell elites, and surface empty cells as explicit generation prompts ('produce a functional, zero-dependency variant') to force coverage.
- LLM-as-interestingness gate (OMNI): before committing effort to a direction, prompt the model to rate it on feasibility (learnable now) AND interestingness (novel vs an explicit log of already-tried approaches, and worthwhile). Only pursue directions that clear both, preventing both mode-collapse and trivial wandering.
- LLM-as-mutation-operator loop (ELM/FunSearch): keep an archive/'islands' of working solutions; each iteration sample an elite, instruct the agent to mutate it in a NAMED direction (swap algorithm/data structure/tradeoff), evaluate with tests, and re-bin. Use best-shot island prompting (show the current best variants as context) to bootstrap increasingly novel-yet-correct solutions.
- AI-feedback QD for fuzzy tasks (QDAIF/QDHF): for writing/design/ideation, define diversity axes in natural language and use the model itself to (a) propose variants pushing toward under-filled regions and (b) score quality and pairwise distance-from-archive via rubric prompts — yielding a covered creative space instead of one safe draft.
- Go-Explore-style state archive with backtracking (IGE): give the agent an explicit archive of promising partial states (repo snapshots, plan branches, reasoning frontiers); each step the model scores which archived state is most interesting to RESUME from, returns there, explores a few actions, and flags serendipitous results to archive — converting a linear agent into a tree explorer that can back up instead of tunnel-visioning the first path.
- Self-curriculum / stepping-stone generator (POET/OMNI-EPIC): maintain a code-defined archive of solved and attempted tasks; an LLM proposes the next task as an executable spec/test that is just-beyond-current-ability and novel vs the archive; retain informative FAILURES as stepping stones. Periodically attempt transferring the current best solution onto a sibling open sub-problem (POET transfer) to unlock stalled progress.
- Explicit anti-mode-collapse selection step: institutionalize a rule that the agent must generate multiple genuinely distinct candidates (verified distinct by an AI-feedback diversity check) before converging, and must justify the chosen one against the alternatives — making divergence a required phase of the loop rather than an afterthought.

### Papers

#### 1. [Abandoning Objectives: Evolution Through the Search for Novelty Alone](https://stars.library.ucf.edu/facultybib2010/1530/)

- **Authors:** Joel Lehman, Kenneth O. Stanley  
- **Year / venue:** — · — · non-arXiv  
- **Verification:** ✅ verified real — via `WebFetch UCF library record (stars.library.ucf.edu); arxiv has no id for this paper` (Confirmed via the UCF STARS faculty bibliography record: title, authors (Joel Lehman, Kenneth O. Stanley), year 2011, journal Evolutionary Computation all match. No arXiv id exists for this journal paper.)

- **Method.** Replace the fitness/objective function entirely with a 'novelty' reward: each candidate is scored by how different its BEHAVIOR is from prior behaviors stored in an archive (k-nearest-neighbor distance in a behavior-characterization space). Search chases behavioral diversity, not the goal.
- **Why it matters for divergence.** The foundational argument that optimizing directly for the objective is often DECEPTIVE and gets stuck in local optima, whereas explicitly rewarding behavioral novelty discovers the stepping stones that actually lead somewhere. This is the core theoretical license for an agent to deliberately NOT pick the highest-probability next move.
- **→ Harness application.** Add a 'behavior characterization' step to the agent loop: after each candidate solution/plan, summarize it into a compact behavior descriptor (e.g. a vector of approach tags or an embedding), keep an archive of past descriptors, and score new candidates by distance-to-k-nearest in the archive rather than by predicted-success alone. A skill could force-generate N candidates, embed them, and explicitly select the most novel-yet-viable one instead of the modal one.

#### 2. [Illuminating Search Spaces by Mapping Elites (MAP-Elites)](https://arxiv.org/abs/1504.04909)

- **Authors:** Jean-Baptiste Mouret, Jeff Clune  
- **Year / venue:** — · — · arXiv:1504.04909  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/1504.04909` (Title and authors match exactly (the official arxiv title uses 'mapping elites'; 'MAP-Elites' is the algorithm name).)

- **Method.** Define a small set of human-chosen 'behavior dimensions' that tessellate a grid; for each cell keep only the single highest-performing solution found with that behavior. The result is a map ('illumination') of the best solution at every point in the diversity space, not one global winner.
- **Why it matters for divergence.** Turns 'find the best answer' into 'fill a grid of qualitatively different best answers,' guaranteeing coverage of the design space. Directly counters mode-collapse: the agent is rewarded for occupying empty cells (unexplored kinds of solutions), which is exactly divergence from the single most-likely prediction.
- **→ Harness application.** Build a MAP-Elites skill where the user (or the agent) names 2-3 axes of variation for a task (e.g. for code: paradigm x dependency-footprint x complexity; for writing: tone x structure x length). The agent maintains a literal grid file; each generated candidate is binned by its descriptor and only kept if it beats the current occupant of that cell. Empty/under-filled cells become explicit prompts ('generate a solution that is functional+zero-dependency'), forcing breadth.

#### 3. [Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions](https://arxiv.org/abs/1901.01753)

- **Authors:** Rui Wang, Joel Lehman, Jeff Clune, Kenneth O. Stanley  
- **Year / venue:** — · — · arXiv:1901.01753  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/1901.01753` (Title and authors match exactly.)

- **Method.** Co-evolve a population of (environment, agent) pairs: the system invents new challenges at the same time it solves them, and crucially TRANSFERS solutions across pairs so a solution to one problem becomes a stepping stone for a harder, different problem. Novelty + minimal-criterion gating keeps the generated curriculum diverse and learnable.
- **Why it matters for divergence.** Shows that progress on hard problems comes from a growing archive of diverse intermediate problems plus cross-pollination of partial solutions — not from hammering one objective. The 'transfer between stepping stones' idea is a concrete mechanism for an agent to escape local optima by borrowing solutions from a sibling sub-problem.
- **→ Harness application.** An agent loop that maintains an archive of (sub-problem, best-attempt) pairs and periodically tries transferring the current best attempt onto a DIFFERENT open sub-problem to see if it unlocks progress. Pair a 'problem-poser' sub-agent (invents adjacent, slightly-harder variants) with a 'solver' sub-agent, gated by a minimal-criterion check (must be non-trivial but not impossible) to auto-generate a self-curriculum.

#### 4. [Evolution through Large Models (ELM)](https://arxiv.org/abs/2206.08896)

- **Authors:** Joel Lehman, Jonathan Gordon, Shawn Jain, Kamal Ndousse, Cathy Yeh, Kenneth O. Stanley  
- **Year / venue:** — · — · arXiv:2206.08896  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2206.08896` (Title and authors match exactly (ELM is the acronym).)

- **Method.** Use an LLM trained on code diffs as an intelligent MUTATION operator inside an evolutionary/MAP-Elites loop: instead of random perturbation, the LLM proposes plausible, meaningful edits to existing programs, and MAP-Elites collects the resulting diverse, functional variants (e.g. hundreds of thousands of Sodarace robots the base model had never seen).
- **Why it matters for divergence.** Demonstrates the LLM is far more powerful as a diversity-generating mutation engine inside a QD archive than as a one-shot answer generator. Pairing 'LLM proposes intelligent variation' with 'archive enforces diversity' is the template for converting a coding agent from a predictor into a divergent explorer.
- **→ Harness application.** Wrap the coding agent as a mutation operator: feed it an existing solution plus an instruction to 'mutate this in a specific direction' (change algorithm, change data structure, change tradeoff), then bin each mutant into a MAP-Elites archive. Iterate: sample a random elite from the archive, mutate it, re-bin. This produces a deliberately diverse library of working variants rather than one greedy implementation.

#### 5. [OMNI: Open-endedness via Models of human Notions of Interestingness](https://arxiv.org/abs/2306.01711)

- **Authors:** Jenny Zhang, Joel Lehman, Kenneth Stanley, Jeff Clune  
- **Year / venue:** — · — · arXiv:2306.01711  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2306.01711` (Title and authors match exactly.)

- **Method.** Use a foundation model as a 'model of interestingness' (MoI) to prioritize, among all learnable tasks, those that are also INTERESTING — i.e. worthwhile and sufficiently novel relative to what the agent already mastered — solving the open-endedness bottleneck of countless-but-boring learnable tasks.
- **Why it matters for divergence.** Pinpoints the exact failure mode of pure novelty (most novel things are trivial/boring) and shows an LLM can supply human-aligned taste to steer divergence toward MEANINGFUL novelty. This is the missing 'is this actually worth exploring?' filter for an agent that would otherwise either collapse to the obvious or wander into useless variation.
- **→ Harness application.** Add an LLM-as-interestingness-judge gate to any exploration loop: before spending effort on a candidate direction, prompt the model to rate it on (a) learnable/feasible given current state and (b) interesting = novel vs the archive AND worthwhile. Only pursue candidates that clear both. Maintain a running log of 'already-mastered' approaches so the judge can score novelty relative to actual history.

#### 6. [Quality-Diversity through AI Feedback (QDAIF)](https://arxiv.org/abs/2310.13032)

- **Authors:** Herbie Bradley, Andrew Dai, Hannah Teufel, Jenny Zhang, Koen Oostermeijer, Marco Bellagente, Jeff Clune, Kenneth Stanley, Gregory Schott, Joel Lehman  
- **Year / venue:** — · — · arXiv:2310.13032  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2310.13032` (Title and authors match (QDAIF acronym; candidate listed first four authors + 'et al.', full author list confirmed).)

- **Method.** Run a QD evolutionary loop entirely on text where the LLM does BOTH jobs: generates variation (mutates/crosses candidate texts) and evaluates quality and diversity via natural-language AI feedback prompts, removing the need for hand-coded quality/diversity metrics. Applied to creative writing (opinions, stories, poetry).
- **Why it matters for divergence.** Solves the practical blocker for QD in qualitative/open-ended domains — you can ask the model, in plain language, 'how different is this from these others?' and 'how good is it?'. This makes novelty-search and MAP-Elites usable for fuzzy domains (writing, design, research ideas) where no numeric fitness exists, which is precisely where coding/general agents need to diverge.
- **→ Harness application.** Implement QD for non-numeric tasks: define diversity axes in natural language, then in the loop ask the model itself to (1) propose a variant pushing toward an under-filled region and (2) score each candidate's quality and its distance from archived candidates via rubric prompts. The archive plus AI-feedback scoring lets a writing/ideation skill systematically cover a creative space instead of returning one safe draft.

#### 7. [Intelligent Go-Explore: Standing on the Shoulders of Giant Foundation Models](https://arxiv.org/abs/2405.15143)

- **Authors:** Cong Lu, Shengran Hu, Jeff Clune  
- **Year / venue:** — · — · arXiv:2405.15143  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2405.15143` (Title and authors match exactly; published at ICLR 2025.)

- **Method.** Replace Go-Explore's hand-designed heuristics with a foundation model that judges which archived states are most interesting/promising to RETURN to, which actions to take when exploring from them, and recognizes serendipitous discoveries — combining the 'remember promising states, return, then explore' archive with LLM taste.
- **Why it matters for divergence.** A direct recipe for an agent loop that explicitly avoids greedy depth-first commitment: keep an archive of reached states, and use the model's own notion of interestingness to decide where to back up to and branch. Beats RL baselines and beats Reflexion on tasks where pure forward reasoning fails — i.e. exactly where single-trajectory agents get stuck.
- **→ Harness application.** Give the agent an explicit state archive (snapshots of promising partial solutions / repo states / reasoning frontiers). Each step: the model scores archived states for 'most interesting to resume from,' the agent returns to that state (not necessarily the latest one), explores a few actions, and flags surprising outcomes worth archiving. This converts a linear agent into a tree/archive explorer with backtracking — preventing tunnel-vision on the first plausible path.

#### 8. [OMNI-EPIC: Open-endedness via Models of human Notions of Interestingness with Environments Programmed in Code](https://arxiv.org/abs/2405.15568)

- **Authors:** Maxence Faldor, Jenny Zhang, Antoine Cully, Jeff Clune  
- **Year / venue:** — · — · arXiv:2405.15568  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2405.15568` (Title and authors match exactly; ICLR 2025.)

- **Method.** Foundation models autonomously write CODE that specifies the next task/environment, chosen to be both learnable (right difficulty for current skills) and interesting (novel vs an archive). Successful tasks become stepping stones for harder ones; failed tasks inform feasible next tasks — an ever-expanding code-defined task archive.
- **Why it matters for divergence.** Closes the open-ended loop entirely in code: the system invents its own increasingly diverse, interesting challenges and keeps an archive of stepping-stones, exactly the architecture for an agent that endlessly generates and tackles novel-but-grounded problems rather than terminating at the first answer.
- **→ Harness application.** A self-curriculum skill: the agent maintains a code-defined archive of tasks it has solved/attempted; an LLM proposes the next task as an executable spec/test that is interesting (novel vs archive) and learnable (just beyond current ability), the agent attempts it, and outcomes (pass/fail + behavior descriptor) update the archive. Failed-but-informative attempts are explicitly retained as stepping stones, mirroring OMNI-EPIC's success+failure archive.


---

## 4. LLM-driven evolution & program/idea search

<a id='4-llm-evolution'></a>

*LLM-driven evolution & program/idea search*

**Key takeaways**

- Novelty comes from the OUTER LOOP, not a single forward pass: every method here gets superhuman/novel results by sampling many LLM variants and applying hard selection — the LLM is the variation operator, an external evaluator is the truth signal. The agent's job is to generate many candidates cheaply and let a scorer decide.
- A reliable, automatable fitness function is the precondition. FunSearch, Eureka, EoH, and AlphaEvolve all work only because the domain has a fast programmatic evaluator. Before evolving, build/define the scorer; without it the loop has no direction and mode-collapse returns.
- Explicitly demand difference. EoH's strongest operator literally instructs the model to produce a heuristic 'totally different' from prior ones; LMX and ELM diversify via parents/niches. Telling the model to diverge — and giving it the prior attempts to diverge FROM — is more effective than hoping temperature alone produces novelty.
- Quality-DIVERSITY beats pure quality for discovery. MAP-Elites (ELM) and island models (FunSearch) keep many distinct good solutions in different behavioral niches, preventing premature convergence. Optimizing only the single best score collapses the search; maintaining a diverse archive sustains exploration.
- Memory of past attempts turns one inference into a search step. OPRO (score-sorted trajectory), Eureka (reward reflection), and AlphaEvolve (program database in-context) all feed the history of attempts-and-outcomes back into the prompt, letting the model infer the improvement direction rather than restart from its prior mean.
- Separate idea-space from implementation-space. EoH co-evolves a natural-language 'thought' plus code; reasoning about WHICH idea is novel in language, then implementing it, yields more divergent solutions than mutating code diffs directly.
- Meta-evolution compounds gains. Promptbreeder evolves its own mutation operators; AlphaEvolve mixes an ensemble of models/settings. Diversifying HOW you mutate — not just what you mutate — keeps the search productive over long horizons.

**Harness mechanisms this theme suggests**

- Evolve-mode skill: given a problem + a runnable scorer, maintain a persistent archive of top-k candidate programs; each generation, build a best-shot prompt (2-3 prior solutions sorted worst→best) and ask Claude for a strictly-better variant; accept only if it beats the archive. The FunSearch/AlphaEvolve core loop as a reusable Claude Code command.
- Island/archive persistence on disk: run several independent archives ('islands') that occasionally reseed from the global best, so different runs explore different algorithmic families and resist mode collapse over long sessions.
- MAP-Elites behavioral grid: define 2-3 descriptors (code size, algorithm family, dependency count, time complexity class), bin every candidate, keep the best per cell, and seed new mutations from deliberately diverse cells — surfacing unconventional but viable solutions the top-1 search would discard.
- Operator library with named mutation prompts: implement EoH's E1/E2/M1/M2/M3 plus Promptbreeder thinking-styles as a rotating set; alternate novelty-seeking ('design something provably different from all prior attempts') with refinement operators on a schedule, and log which operator produced each score gain.
- Reflection channel: have the evaluator emit component-level telemetry, auto-summarize it into a textual critique (Eureka-style), and feed that — not just the scalar score — into the next generation's prompt so edits are targeted rather than random.
- LMX crossover tool: select 3-5 high-fitness, mutually-distinct parents (one per archive niche), present them as unlabeled few-shot examples, and ask Claude for 'another in the same spirit' to recombine their features.
- OPRO ledger wrapper: a lightweight decorator around any agent step with a numeric objective that injects a score-sorted history of past attempts into the prompt and requests a candidate expected to beat them all — cheap memory-as-search add-on.
- Meta-mutation step: periodically ask Claude to invent NEW mutation operators based on which past operators yielded improvements (Promptbreeder self-reference), and persist the evolving operator set across sessions.
- Evaluator cascade: gate expensive full benchmarks behind fast smoke tests so many candidates can be screened in parallel/background (AlphaEvolve), maximizing the number of LLM variants the loop can afford to try per unit time.

### Papers

#### 1. [Mathematical discoveries from program search with large language models (FunSearch)](https://www.nature.com/articles/s41586-023-06924-6)

- **Authors:** B. Romera-Paredes, M. Barekatain, A. Novikov, M. Balog, M. P. Kumar, E. Dupont, F. J. R. Ruiz, J. Ellenberg, P. Wang, O. Fawzi, P. Kohli, A. Fawzi  
- **Year / venue:** 2023 · Nature · Nature  
- **Verification:** ✅ verified real — via `semanticscholar search` (Confirmed via Semantic Scholar; Nature 2023, DOI 10.1038/s41586-023-06924-6, matching the claimed URL and authors.)

- **Method.** Pairs a pretrained LLM (sampling code mutations from a best-shot prompt of prior high-scoring programs) with a deterministic evaluator, inside an islands-based evolutionary loop that evolves the PROGRAM that generates a solution rather than the solution itself.
- **Why it matters for divergence.** Demonstrates that an LLM's most-likely output is not the ceiling: by sampling many low-temperature variants and keeping only the rare ones that score better against a hard evaluator, the system found genuinely new mathematics (cap set, bin packing) beyond anything in training data. Novelty comes from selection pressure over many samples, not from any single clever generation.
- **→ Harness application.** Build a Claude Code skill that, given a problem with a programmatic scorer, maintains a small archive of the top-k scoring solution-functions, builds a 'best-shot' prompt showing 2 prior programs sorted worst→best, asks Claude to write a strictly-better v3, runs the evaluator, and keeps it only if it beats the archive. Use multiple 'islands' (separate archives reseeded periodically from the global best) to prevent premature convergence on one approach.

#### 2. [Evolution of Heuristics: Towards Efficient Automatic Algorithm Design Using Large Language Model (EoH)](https://arxiv.org/abs/2401.02051)

- **Authors:** Fei Liu, Xialiang Tong, Mingxuan Yuan, Xi Lin, Fu Luo, Zhenkun Wang, Zhichao Lu, Qingfu Zhang  
- **Year / venue:** 2024 · ICML 2024 · arXiv:2401.02051  
- **Verification:** ✅ verified real — via `arxiv id_list` (arXiv:2401.02051 title and authors match exactly.)

- **Method.** Co-evolves a natural-language 'thought' describing a heuristic AND its executable code; uses five explicitly different LLM prompt operators (two exploration 'E1/E2' that demand novelty vs. existing ideas, three modification 'M1/M2/M3') to mutate/crossover a population, selecting on benchmark fitness.
- **Why it matters for divergence.** The key divergence mechanism is forcing the LLM to first articulate a DIFFERENT idea in language ('produce a heuristic that is totally different from the given ones'), then implement it — separating idea-space exploration from code generation. This directly counters mode collapse where the model re-emits the obvious algorithm.
- **→ Harness application.** Encode the five EoH operators as named prompt templates in a skill. The 'E1' operator explicitly instructs Claude: 'study these N existing approaches, then design one whose core mechanism is provably distinct from all of them.' Alternate exploration operators (novelty-seeking) with modification operators (refine the current best) on a schedule, and store the natural-language 'thought' alongside each candidate so later prompts can reason about idea diversity, not just code diffs.

#### 3. [Promptbreeder: Self-Referential Self-Improvement Via Prompt Evolution](https://arxiv.org/abs/2309.16797)

- **Authors:** Chrisantha Fernando, Dylan Banarse, Henryk Michalewski, Simon Osindero, Tim Rocktäschel  
- **Year / venue:** 2023 · arXiv (DeepMind) · arXiv:2309.16797  
- **Verification:** ✅ verified real — via `arxiv id_list` (arXiv:2309.16797 title and authors match exactly.)

- **Method.** Evolves a population of task-prompts via LLM-driven mutation, where the mutation-prompts themselves also evolve (self-referential), plus a library of ~9 'thinking styles' and hyper-mutation operators that diversify how mutation happens.
- **Why it matters for divergence.** Shows divergence can be injected at the meta level: instead of one fixed mutation strategy, the system maintains and evolves a diverse pool of mutation operators and thinking styles, so the search keeps generating qualitatively new directions rather than collapsing to one improvement pattern.
- **→ Harness application.** Give a Claude Code self-improvement loop a rotating library of mutation strategies ('rephrase as constraints', 'invert an assumption', 'borrow a method from an unrelated field') and a meta-step where Claude periodically writes NEW mutation strategies based on which past ones produced score gains. Persist both the candidate prompts/solutions and the mutation operators that created them across runs.

#### 4. [Eureka: Human-Level Reward Design via Coding Large Language Models](https://arxiv.org/abs/2310.12931)

- **Authors:** Yecheng Jason Ma, William Liang, Guanzhi Wang, De-An Huang, Osbert Bastani, Dinesh Jayaraman, Yuke Zhu, Linxi Fan, Anima Anandkumar  
- **Year / venue:** 2023 · ICLR 2024 · arXiv:2310.12931  
- **Verification:** ✅ verified real — via `arxiv id_list` (arXiv:2310.12931 title and authors match exactly.)

- **Method.** Evolutionary search over reward-function code: samples many reward programs from GPT-4 conditioned on raw environment source, trains RL policies to evaluate them, and uses 'reward reflection' (textual feedback summarizing per-component training statistics) to guide the next generation of mutations.
- **Why it matters for divergence.** Introduces structured textual-gradient feedback: rather than a scalar fitness, the LLM receives a rich, automatically generated critique of WHY the last candidate underperformed, letting it make targeted, non-obvious edits. Sampling-plus-reflection beats human experts on 83% of tasks.
- **→ Harness application.** For any optimization where the evaluator emits component-level telemetry (test pass rates, latency per function, sub-scores), feed Claude an auto-summarized 'reflection' of those signals between generations rather than just the total score. Sample K candidate programs per generation in parallel, evaluate all, then have Claude reflect on the best+worst and propose the next batch — exploiting parallel breadth plus diagnostic feedback.

#### 5. [Evolution through Large Models (ELM)](https://arxiv.org/abs/2206.08896)

- **Authors:** Joel Lehman, Jonathan Gordon, Shawn Jain, Kamal Ndousse, Cathy Yeh, Kenneth O. Stanley  
- **Year / venue:** 2022 · arXiv (OpenAI) / book chapter · arXiv:2206.08896  
- **Verification:** ✅ verified real — via `arxiv abs page` (arXiv:2206.08896 title and authors match (arxiv id_list endpoint was rate-limited; verified via arxiv.org/abs page).)

- **Method.** Uses an LLM fine-tuned on code diffs as an intelligent mutation operator inside MAP-Elites (a quality-diversity algorithm), generating hundreds of thousands of functional Sodarace robot programs spanning a behavioral grid the base model never saw.
- **Why it matters for divergence.** Foundational argument that LLM mutations are 'intelligent' (semantically plausible edits humans would make) rather than random, and that pairing them with a quality-DIVERSITY archive (MAP-Elites) deliberately rewards behavioral novelty across many niches instead of converging to a single optimum — the core anti-mode-collapse mechanism.
- **→ Harness application.** Add a MAP-Elites-style archive to an agent loop: define 2-3 behavioral descriptors for solutions (e.g., code length, algorithmic family, dependency footprint), bin candidates into that grid, and keep the best per cell. When prompting Claude for the next mutation, seed from a deliberately diverse set of cells (not just the global best) so the search fills distinct niches and surfaces unconventional solutions.

#### 6. [AlphaEvolve: A coding agent for scientific and algorithmic discovery](https://arxiv.org/abs/2506.13131)

- **Authors:** Alexander Novikov, Ngân Vũ, Marvin Eisenberger, Emilien Dupont, Po-Sen Huang, Adam Zsolt Wagner, Sergey Shirobokov, Borislav Kozlovskii, Francisco J. R. Ruiz, Abbas Mehrabian, M. Pawan Kumar, et al. (Google DeepMind)  
- **Year / venue:** 2025 · Google DeepMind (technical report) / arXiv · arXiv:2506.13131  
- **Verification:** ✅ verified real — via `semanticscholar search` (Candidate had no arxiv_id (cited DeepMind blog). Semantic Scholar confirms the paper exists as arXiv:2506.13131 (2025); arxiv_id/url corrected accordingly.)

- **Method.** An evolutionary coding agent that evolves entire codebases (not just single functions) via an ensemble of Gemini models proposing diffs, an automated-evaluator cascade, and a program database balancing exploration/exploitation; discovered a faster 4x4 complex matrix-multiplication algorithm and improved data-center scheduling.
- **Why it matters for divergence.** Scales the FunSearch idea from single functions to whole programs and from one model to a model ensemble, and shows asynchronous, parallel evaluation with rich prompt context (past attempts, evaluation results) lets the loop reach results beyond expert humans on open problems — concrete proof the evolutionary outer loop is the source of frontier novelty.
- **→ Harness application.** Architect a long-running Claude Code 'evolve' mode: a persistent program database, diff-based mutations (Claude edits marked code blocks rather than rewriting whole files), a fast→slow cascade of evaluators (quick smoke tests gate expensive full benchmarks), and a controller that mixes proposals from different model settings/temperatures. Run evaluation asynchronously in the background so many candidates are in flight at once.

#### 7. [Large Language Models as Optimizers (OPRO)](https://arxiv.org/abs/2309.03409)

- **Authors:** Chengrun Yang, Xuezhi Wang, Yifeng Lu, Hanxiao Liu, Quoc V. Le, Denny Zhou, Xinyun Chen  
- **Year / venue:** 2023 · ICLR 2024 · arXiv:2309.03409  
- **Verification:** ✅ verified real — via `arxiv abs page` (arXiv:2309.03409 title and authors match (verified via arxiv.org/abs page after id_list rate-limit).)

- **Method.** Describes the optimization task in natural language and iteratively prompts the LLM with a 'meta-prompt' containing the trajectory of past solution→score pairs sorted by value; the LLM proposes new solutions, which are scored and appended, performing gradient-free optimization-by-prompting.
- **Why it matters for divergence.** Shows that simply exposing the LLM to its own history of attempts-with-scores lets it infer the direction of improvement and propose solutions better than human-designed ones — a lightweight way to make a forward pass behave like a step of search by giving it memory of the optimization landscape.
- **→ Harness application.** For tuning tasks (prompt wording, config params, thresholds), maintain a running ledger of (candidate, score) pairs and inject the top-N sorted ascending into each new request to Claude, explicitly asking for a candidate expected to outscore them all. Cheap to bolt onto any agent step that has a numeric objective; keep temperature up to maintain proposal diversity and cap the ledger to recent/best entries.

#### 8. [Language Model Crossover: Variation through Few-Shot Prompting (LMX)](https://arxiv.org/abs/2302.12170)

- **Authors:** Elliot Meyerson, Mark J. Nelson, Herbie Bradley, Adam Gaier, Arash Moradi, Amy K. Hoover, Joel Lehman  
- **Year / venue:** 2023 · ACM TELO · arXiv:2302.12170  
- **Verification:** ✅ verified real — via `arxiv abs page` (arXiv:2302.12170 title and authors match (verified via arxiv.org/abs page after id_list rate-limit).)

- **Method.** Implements evolutionary crossover by concatenating several parent solutions into a few-shot prompt and sampling the LLM's continuation as offspring; the in-context pattern-completion naturally recombines parent traits across domains (strings, equations, sentences, prompts, Python).
- **Why it matters for divergence.** Gives a domain-agnostic recombination operator: putting multiple diverse parents in-context biases the model toward outputs that blend their distinct features rather than regressing to its single prior-mean output, a direct mechanism for combinatorial novelty from existing good solutions.
- **→ Harness application.** Add a 'crossover' tool to an agent loop: select 3-5 high-fitness but mutually different prior solutions, present them as unlabeled few-shot examples, and ask Claude to generate 'another solution in the same spirit' — yielding recombinations. Pair with parent selection that maximizes diversity (e.g., pick parents from different archive niches) so crossover explores between attractors instead of within one.


---

## 5. Structured reasoning & search at inference time

<a id='5-inference-search'></a>

*Structured reasoning & search at inference time*

**Key takeaways**

- The single greedy chain is the core failure mode; every method here replaces 'commit to most-likely next token/step' with generate-many + evaluate + select/backtrack.
- Divergence has three distinct levers: (1) sample width — diverse paths (self-consistency, best-of-N); (2) structure — branch with backtracking (ToT) or recombine across branches (GoT); (3) depth — sequential self-revision of one line (R1-style, Snell's revision axis).
- Search is only as good as the selector. A verifier / value function (PRM, LM self-eval, or real test feedback) is what converts many candidates into a better answer — without it, wide sampling just adds noise.
- Ground the reward in external signals when possible. LATS and coding agents get reliable rewards from running tests/builds; pure self-evaluation (ToT/GoT) is weaker and can confidently mis-rank — prefer executable verification over LM opinion.
- Compute allocation should be difficulty-aware (Snell): easy tasks -> deepen one chain via revision; hard tasks -> widen the search. Always-on fixed best-of-N wastes budget on easy work and under-searches hard work.
- Failed branches are information, not waste (Reflexion): a structured 'why it failed, so try a different axis' note enforces genuine diversity across retries instead of re-sampling near the same wrong attempt.
- Recombination, not just branching, produces novelty (GoT): merging the best parts of independent solution branches yields answers no single chain reaches.
- The newest models (R1) can perform explore/verify/backtrack in-context, so a harness can often elicit deliberate search via scaffolding prompts and only escalate to external tree machinery for the hardest problems.

**Harness mechanisms this theme suggests**

- Branch-and-verify skill: at any high-stakes decision (architecture, root-cause, fix strategy), fan out k parallel sub-agents at elevated temperature, score each candidate with a verifier sub-agent grounded in real tests/build, and keep a frontier of top-b — the explicit ToT/best-of-N loop for code.
- Persistent search-tree state file (JSON/markdown): store the frontier, each node's candidate edit, eval score, and reflection, so backtracking and explore/exploit decisions survive context resets and the agent can pop back to an abandoned-but-promising branch.
- Difficulty router (Snell-inspired): a cheap pre-step rates task hardness and chooses strategy — single chain + sequential self-revision for easy tasks, wide MCTS/best-of-N for hard ones — with an explicit compute budget the controller spends where marginal gain is highest.
- MCTS-over-tools loop (LATS): nodes = repo states, expansions = candidate commands/edits, reward = actual test/build/lint outcomes backpropagated, selection via UCB (LM value + exploration bonus for under-tried branches) to ground search in real feedback rather than self-judgment.
- Diversity-enforcing retry wrapper (Reflexion): on verification failure, force a structured reflection note and require the next attempt to differ in approach from all prior attempts, using the reflection log as the explicit anti-duplication constraint.
- Merge/aggregate operation (GoT): after exploring 2-3 independent branches, run a synthesis step that extracts the best component from each into a hybrid solution, plus a refine-loop edge that iterates critique->improve until a quality bar is met.
- Step-level verifier sub-agent (PRM): a reusable scoring function that emits per-step pass/fail + aggregate score for any plan or patch, used both to rank best-of-N outputs and to prune weak partial branches mid-search, with step scores tied to concrete checks (typecheck, spec match, invariant preservation).
- Inline deliberation prompt template (R1): for planning phases, require 'enumerate >=3 distinct approaches, red-team each, choose, then verify against constraints before any edit' with a long-thinking budget — cheap divergence that precedes external search machinery.

### Papers

#### 1. [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)

- **Authors:** Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou  
- **Year / venue:** 2022 · ICLR 2023 / arXiv · arXiv:2203.11171  
- **Verification:** ✅ verified real — via `arxiv API id_list=2203.11171` (Title and authors match exactly.)

- **Method.** Instead of greedy decoding a single chain, sample a DIVERSE set of reasoning paths at higher temperature and marginalize: take the answer that the most independent paths agree on (majority vote over latent reasoning).
- **Why it matters for divergence.** The foundational 'don't trust one chain' result. A complex problem admits many distinct correct derivations; sampling diverse paths and voting directly counters the single-most-likely-prediction failure mode and recovers correct answers the greedy path misses (+17.9% GSM8K).
- **→ Harness application.** A skill that runs the agent's plan/diagnosis step N times in parallel sub-agents at elevated temperature, then clusters the candidate answers (e.g., by final patch hunk, by chosen API, by root-cause hypothesis) and surfaces the plurality cluster plus dissenting minority. For code where 'answers' aren't identical strings, vote on a normalized signature (test outcome, function chosen, file touched) rather than verbatim text.

#### 2. [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)

- **Authors:** Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L. Griffiths, Yuan Cao, Karthik Narasimhan  
- **Year / venue:** 2023 · NeurIPS 2023 · arXiv:2305.10601  
- **Verification:** ✅ verified real — via `arxiv API id_list=2305.10601` (Title and authors match exactly.)

- **Method.** Generalizes chain-of-thought into a search tree: at each step generate multiple candidate 'thoughts', have the LLM self-evaluate each (sure/maybe/impossible or value score), then traverse with BFS/DFS, pruning dead branches and backtracking.
- **Why it matters for divergence.** The canonical mechanism for deliberate branching exploration with lookahead and backtracking — the antidote to token-level left-to-right commitment. Game of 24 jumped from 4% (CoT) to 74% precisely because the model could abandon bad early commitments and try alternatives.
- **→ Harness application.** A harness loop with explicit state: at each decision point (architecture choice, fix strategy, refactor approach) spawn k candidate 'thoughts', run a self-eval prompt that rates each as promising/uncertain/dead-end, keep the top-b in a frontier, and DFS the best while retaining the ability to pop back to the frontier when tests fail. Persist the frontier as a JSON tree so backtracking survives context resets.

#### 3. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)

- **Authors:** Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao  
- **Year / venue:** 2023 · NeurIPS 2023 · arXiv:2303.11366  
- **Verification:** ✅ verified real — via `arxiv API id_list=2303.11366` (Title and authors match exactly.)

- **Method.** After a failed attempt, the agent verbally reflects on the feedback signal (test failure, error trace), writes a self-critique into an episodic memory buffer, and conditions the next attempt on those reflections — reinforcement via language, not weights.
- **Why it matters for divergence.** Turns each failed branch into information that steers the NEXT branch somewhere genuinely different, rather than re-sampling near the same failure. Prevents the agent from looping on the same most-likely-but-wrong approach by forcing an explicit 'why that failed, try a different axis' step.
- **→ Harness application.** A retry wrapper that, on any verification failure (failing test, lint, runtime error), forces a structured reflection note ('hypothesis was X, evidence Y disproves it, therefore avoid X-family approaches') appended to a persistent REFLECTIONS.md fed into the next attempt's context. Crucially gate retries so attempt n+1 must differ in approach from attempts 1..n, using the reflection log as the diversity constraint.

#### 4. [Graph of Thoughts: Solving Elaborate Problems with Large Language Models](https://arxiv.org/abs/2308.09687)

- **Authors:** Maciej Besta, Nils Blach, Ales Kubicek, Robert Gerstenberger, Michal Podstawski, Lukas Gianinazzi, Joanna Gajda, Tomasz Lehmann, Hubert Niewiadomski, Piotr Nyczyk, Torsten Hoefler  
- **Year / venue:** 2023 · AAAI 2024 · arXiv:2308.09687  
- **Verification:** ✅ verified real — via `arxiv API id_list=2308.09687` (Title matches; full author list confirmed (candidate used 'et al.').)

- **Method.** Models thoughts as vertices in an arbitrary graph rather than a tree, enabling aggregation (merging several thoughts into one), refinement loops, and distillation — not just branching but recombining partial solutions.
- **Why it matters for divergence.** Divergence isn't only about branching wide; novelty often comes from MERGING ideas from separate branches. GoT adds aggregation/feedback edges, letting an agent synthesize a solution no single chain would produce, and reports +62% sort quality with >31% lower cost vs ToT.
- **→ Harness application.** A skill that explicitly supports a 'merge' operation: after exploring 2-3 independent solution branches (e.g., three different module designs from parallel sub-agents), run an aggregation prompt that extracts the best component from each and synthesizes a hybrid, plus a 'refine' edge that loops a candidate through critique-improve until a quality threshold. Model the workflow as a small DAG of generate/aggregate/refine operations.

#### 5. [Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models (LATS)](https://arxiv.org/abs/2310.04406)

- **Authors:** Andy Zhou, Kai Yan, Michal Shlapentokh-Rothman, Haohan Wang, Yu-Xiong Wang  
- **Year / venue:** 2023 · ICML 2024 · arXiv:2310.04406  
- **Verification:** ✅ verified real — via `arxiv API id_list=2310.04406` (Title and authors match (feed omits commas in title).)

- **Method.** Brings full Monte Carlo Tree Search to LLM agents: selection/expansion/evaluation/backpropagation over a tree of action sequences, using an LM value function and self-reflection, with environment feedback (tool/test results) grounding the rollouts.
- **Why it matters for divergence.** The most principled inference-time search for agentic, multi-step tasks where actions have real external feedback (running code, tests). MCTS's UCB balances exploiting the current best branch against exploring under-tried ones — exactly the explore/exploit tradeoff a greedy coding agent lacks. Achieves 94.4% pass@1 on HumanEval.
- **→ Harness application.** An agent loop implementing MCTS over tool-action sequences: each node = repo state, expansion = a candidate edit/command, the 'reward' = real test/build/lint outcomes, backpropagated to bias future selection. Use a UCB-style score (LM value estimate + exploration bonus for less-visited branches) to decide which partial solution to extend next, and reuse failed-rollout reflections as node annotations.

#### 6. [Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314)

- **Authors:** Charlie Snell, Jaehoon Lee, Kelvin Xu, Aviral Kumar  
- **Year / venue:** 2024 · arXiv (Google DeepMind / UC Berkeley) · arXiv:2408.03314  
- **Verification:** ✅ verified real — via `arxiv API id_list=2408.03314` (Title and authors match exactly.)

- **Method.** Studies how to allocate a fixed test-time compute budget across two axes — parallel search against a verifier (best-of-N / beam / lookahead) vs sequential revision of a single chain — and shows a 'compute-optimal' policy that adapts the strategy to prompt difficulty, beating naive best-of-N by 4x and even larger-model baselines.
- **Why it matters for divergence.** Gives the principled answer to 'how MUCH to diverge and HOW': easy prompts benefit from sequential refinement of one chain, hard prompts from wide parallel search. Tells a harness when branching is worth the cost and when to instead deepen one line — turning divergence into a budgeted, difficulty-aware decision.
- **→ Harness application.** A meta-controller skill that first cheaply estimates task difficulty (LM self-rating + signals like failing-test count / ambiguity), then picks a strategy: low difficulty -> single chain with sequential self-revision; high difficulty -> wide parallel branch-and-verify with a larger N and beam search. Expose a compute budget and let the controller spend it where the marginal gain is highest rather than always running fixed best-of-N.

#### 7. [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948)

- **Authors:** DeepSeek-AI, Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, et al.  
- **Year / venue:** 2025 · Nature 2025 / arXiv · arXiv:2501.12948  
- **Verification:** ✅ verified real — via `arxiv API id_list=2501.12948` (Title matches; lead author DeepSeek-AI / Daya Guo confirmed.)

- **Method.** Shows that pure large-scale RL (without supervised reasoning traces) elicits emergent long-chain behaviors — self-reflection, verification, exploring alternatives, and dynamic strategy switching mid-solution — internalizing search into a single long generation.
- **Why it matters for divergence.** Evidence that the explore/backtrack/self-verify behaviors ToT/LATS impose externally can be elicited as in-context behavior. For a harness this validates prompting/scaffolding the model to 'consider alternatives, then verify, then switch strategy' inline, and to budget long deliberate reasoning before committing to an edit.
- **→ Harness application.** A reasoning-scaffold prompt template for the planning phase that explicitly elicits R1-style moves: 'enumerate at least 3 distinct approaches, red-team each, pick one, then verify your choice against the constraints before writing code.' Pair with a long-thinking budget so the agent diverges and self-checks in-context before any tool call, reserving external tree-search machinery for the hardest tasks.

#### 8. [Process Reward Models That Think (ThinkPRM)](https://arxiv.org/abs/2504.16828)

- **Authors:** Muhammad Khalifa, Rishabh Agarwal, Lajanugen Logeswaran, Jaekyeom Kim, Hao Peng, Moontae Lee, Honglak Lee, Lu Wang  
- **Year / venue:** 2025 · arXiv · arXiv:2504.16828  
- **Verification:** ✅ verified real — via `arxiv API id_list=2504.16828` (Title matches (candidate appended subtitle 'ThinkPRM'). NOTE: candidate authors 'Mukherjee, Kim, et al.' are INCORRECT — actual lead author is Muhammad Khalifa et al.; corrected verified_authors recorded.)

- **Method.** A generative long-CoT verifier that scores a multi-step solution step-by-step (process reward) by reasoning about each step, trained on orders-of-magnitude fewer labels than discriminative PRMs; used to rank candidates in best-of-N and to guide reward-guided search.
- **Why it matters for divergence.** Divergence is only useful if you can pick the good branch. A strong step-level verifier is the selection half of branch-and-search — it lets an agent generate many candidates AND reliably keep the right one, and prunes bad partial branches early during search rather than only judging final answers.
- **→ Harness application.** A verifier sub-agent invoked as the scoring function inside any branching loop: given a candidate plan/patch, it emits a step-by-step critique with a per-step pass/fail and an aggregate score, used both to rank best-of-N candidates and to prune low-scoring partial branches mid-search. In a coding harness, ground its step scores against concrete checks (does this step typecheck / match the spec / preserve invariants) so the reward isn't purely self-judged.


---

## 6. Self-reflection, critique & multi-agent debate

<a id='6-reflection-debate'></a>

*Self-reflection, critique & multi-agent debate*

**Key takeaways**

- Reflection polishes, debate diverges. Single-model iterative self-critique (Self-Refine, Reflexion) reliably improves surface quality and catches errors against an external signal, but it tends to redistribute within the model's existing idea rather than find a new one. Genuine novelty in this literature comes from enforced disagreement across independent vantage points.
- Degeneration-of-Thought is the core failure mode (Liang et al.): once an LLM is confident in its first answer, reflection rationalizes rather than revises it. The fix is structural — adversarial roles ('tit-for-tat') plus a separate judge — not more or better self-reflection prose.
- Intrinsic self-correction can HURT (Huang et al., ICLR'24): with no external/oracle signal, self-correction on reasoning tasks often stays flat or degrades because the model has no reliable internal error detector. Therefore every critique loop in a harness must be gated on real external signal (tests, execution, retrieval, a different model) — never 'reflect again with no new information'.
- Diversity is the active ingredient, not agent count (Hegazy). Heterogeneous models/personas debating beat N identical copies (91% vs 82% on GSM-8K). Identical agents converge to a shared prior; the value of debate is proportional to how genuinely different the participants' starting points are.
- Anchor critique to an explicit rubric (Constitutional AI). Open-ended 'is this good?' self-critique is unreliable; critique against a written constitution/standard is checkable and steerable. A 'novelty constitution' can make a critic actively penalize the obvious, most-likely answer.
- Diverge at the meta level too (Self-Discover): deliberately composing the reasoning structure — and including operators like 'generate alternatives' or 'invert the problem' — steers the model off its default chain at far lower compute than brute-force sampling/self-consistency.
- Practical pipeline shape: DIVERGE first (heterogeneous parallel agents / adversarial debate / structured alternative-generation) to widen the answer space, THEN converge (judge), THEN polish (Self-Refine). Conflating the polish phase with the divergence phase is how harnesses fool themselves into thinking iteration produced novelty.

**Harness mechanisms this theme suggests**

- Devil's-advocate debate skill: spawn an Affirmative agent (defends the current plan/answer) and a Negative agent forbidden from agreeing in early rounds and rewarded for proposing a structurally DIFFERENT approach, plus a Judge agent that scores both on evidence before deciding. Implements Liang et al.'s tit-for-tat + judge to break Degeneration-of-Thought.
- Heterogeneity-maximizing ensemble: before debating, instantiate agents with deliberately distinct personas/models/temperatures/tool-budgets (skeptic, domain expert, contrarian, first-principles thinker), measure inter-agent answer diversity, and if diversity is low, perturb roles BEFORE spending debate rounds — operationalizes Hegazy's finding that diversity, not count, drives gains.
- External-signal gate on all critique loops: a harness rule that forbids 'reflect again with no new information.' Every self-correction iteration must be backed by a fresh external signal (run tests, execute code, fetch docs, query another model); track per-round whether the answer changed and whether it helped, aborting loops that degrade — directly addresses Huang et al.
- Novelty constitution: an explicit written rubric the critic judges against ('reject the first obvious solution; require >=1 non-standard approach; flag if the answer matches the most common known pattern; name the assumption that would have to be false for a different answer to win'). Turns vague self-critique into a checkable, divergence-promoting gate (Constitutional-AI pattern repurposed for novelty).
- Structured divergence pre-step (Self-Discover style): before solving, the agent selects reasoning operators from a library and must always include a divergence operator — 'propose two fundamentally different approaches and argue for each before choosing' — written into an explicit PLAN it then executes.
- Persistent reflection memory with anti-repeat check (Reflexion): a REFLECTIONS.md the agent appends 'wrong assumption + try-instead' notes to after each failure, and a diff-gate that rejects any retry whose plan is too similar to a previously-failed reflection — forcing each attempt to be materially different.
- Three-phase pipeline orchestration: DIVERGE (heterogeneous parallel/adversarial generation) -> CONVERGE (judge synthesizes) -> POLISH (Self-Refine micro-loop), with the polish phase explicitly walled off so quality refinement is never mistaken for exploration. A diversity metric on the diverge phase output decides whether to widen further before converging.

### Papers

#### 1. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)

- **Authors:** Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao  
- **Year / venue:** 2023 · NeurIPS · arXiv:2303.11366  
- **Verification:** ✅ verified real — via `arxiv id_list 2303.11366` (Title and authors match exactly.)

- **Method.** Agents convert task feedback (scalar or free-form, external or self-simulated) into verbal self-reflections stored in an episodic memory buffer, then condition the next attempt on that reflection instead of updating weights.
- **Why it matters for divergence.** Shows that natural-language critique held in memory across trials lets an agent escape a failed trajectory and try a materially different approach — but ONLY when the feedback signal is informative (tests, environment outcome). It is the canonical 'reflect then retry differently' loop; novelty comes from the memory of what failed, not from the reflection prose itself.
- **→ Harness application.** Add a persistent REFLECTIONS.md scratchpad to the agent loop: after any failing test/build/eval, force the agent to write a terse 'what I assumed that was wrong + what to try instead' note, then start the next attempt by reading that file. Cap retries and require each retry's plan to differ from prior reflections (diff-check) so it cannot re-submit a near-identical solution.

#### 2. [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651)

- **Authors:** Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, Peter Clark  
- **Year / venue:** 2023 · NeurIPS · arXiv:2303.17651  
- **Verification:** ✅ verified real — via `arxiv id_list 2303.17651` (Title matches exactly; full author list confirmed (candidate used 'et al.').)

- **Method.** A single LLM acts as generator, then as critic producing actionable feedback on its own output, then as refiner — looped with no extra training or RL until a stopping criterion is met.
- **Why it matters for divergence.** The clearest demonstration of the polish/novelty distinction: Self-Refine reliably raises preference scores on open-ended generation (clarity, structure, style) but mostly redistributes within the same idea — it improves the answer it already had rather than finding a different one. Useful as the 'polish' baseline a divergence harness must beat.
- **→ Harness application.** Use as a final-pass quality gate, NOT an idea generator: run a generator→critic→refiner micro-loop with explicit, dimensioned feedback rubrics (correctness, edge-cases, naming, perf) on already-chosen solutions. Keep it strictly separate from the divergence phase so polishing never masquerades as exploration.

#### 3. [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325)

- **Authors:** Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, Igor Mordatch  
- **Year / venue:** 2023 · arXiv / ICML 2024 · arXiv:2305.14325  
- **Verification:** ✅ verified real — via `arxiv id_list 2305.14325` (Title and authors match exactly.)

- **Method.** Multiple independent LLM instances each produce an answer with reasoning, then over several rounds read each other's responses and revise toward a consensus final answer; identical prompts/procedure across tasks, applicable to black-box models.
- **Why it matters for divergence.** Independent instances reasoning in parallel cover a wider hypothesis space than one chain, and cross-exposure lets correct minorities pull the group off a shared wrong attractor — reducing hallucination. The divergence here is from parallelism + mutual critique, though same-model agents still tend to converge to a shared prior.
- **→ Harness application.** Spawn N parallel sub-agents (Task tool) on the same problem with independent context, have each emit answer+rationale, then run R rounds where each agent revises after reading the others' rationales, and a final reducer synthesizes. Critically: seed each agent differently (different system framing/temperature/tool budget) so they don't all start from the same mode.

#### 4. [Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate](https://arxiv.org/abs/2305.19118)

- **Authors:** Tian Liang, Zhiwei He, Wenxiang Jiao, Xing Wang, Yan Wang, Rui Wang, Yujiu Yang, Shuming Shi, Zhaopeng Tu  
- **Year / venue:** 2023 · EMNLP 2024 · arXiv:2305.19118  
- **Verification:** ✅ verified real — via `arxiv id_list 2305.19118` (Title and authors match exactly.)

- **Method.** Names the 'Degeneration-of-Thought' (DoT) failure — once an LLM is confident, reflection can't generate novel thoughts even when wrong — and counters it with a MAD framework where agents argue 'tit-for-tat' (affirmative vs negative) and a judge moderates and picks the final answer.
- **Why it matters for divergence.** The single most on-theme paper: it directly diagnoses why self-reflection produces polish not novelty (the model defends its first commitment) and shows that *adversarial* roles plus a separate judge break the fixation, yielding genuinely different solutions on tasks needing deep, counter-intuitive reasoning. Also warns that if agents are too agreeable or the judge too lenient, divergence collapses.
- **→ Harness application.** Build a /devils-advocate skill: instantiate an Affirmative agent (defends current plan/answer) and a Negative agent (must attack it and propose a structurally different alternative — forbidden from agreeing in early rounds), plus a Judge agent that scores both on evidence and only then decides. Enforce 'tit-for-tat': the Negative role is rewarded for finding a genuinely distinct approach, preventing premature consensus.

#### 5. [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798)

- **Authors:** Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou  
- **Year / venue:** 2023 · ICLR 2024 · arXiv:2310.01798  
- **Verification:** ✅ verified real — via `arxiv id_list 2310.01798` (Title and authors match exactly.)

- **Method.** Empirical study isolating *intrinsic* self-correction (no oracle/external signal): when the model must judge correctness using only itself, accuracy on reasoning tasks often stays flat or DROPS after self-correction rounds.
- **Why it matters for divergence.** The essential cautionary counterpoint: it proves that critique loops without an external signal are not free novelty — the model lacks a reliable internal 'this is wrong' detector, so it churns or talks itself out of correct answers. This sets the design constraint: divergence harnesses must inject *independent* signal (tests, other models, retrieval, a real judge), not just more self-reflection.
- **→ Harness application.** Make external grounding mandatory in every critique loop: gate self-correction behind a real signal (run the tests, execute the code, fetch a doc, query a different model). Forbid 'reflect again with no new information' iterations — if no new external evidence is available, stop rather than spin. Track whether each correction round changed the answer and whether it helped, to detect degradation.

#### 6. [Self-Discover: Large Language Models Self-Compose Reasoning Structures](https://arxiv.org/abs/2402.03620)

- **Authors:** Pei Zhou, Jay Pujara, Xiang Ren, Xinyun Chen, Heng-Tze Cheng, Quoc V. Le, Ed H. Chi, Denny Zhou, Swaroop Mishra, Huaixiu Steven Zheng  
- **Year / venue:** 2024 · NeurIPS 2024 · arXiv:2402.03620  
- **Verification:** ✅ verified real — via `arxiv id_list 2402.03620` (Title and authors match exactly.)

- **Method.** Before solving, the model SELECTS atomic reasoning modules (e.g., critical thinking, decompose, step-by-step, think about alternatives) from a seed set and COMPOSES them into a task-specific reasoning structure (a JSON plan) that it then follows during decoding.
- **Why it matters for divergence.** Diverges at the meta level: instead of one default chain-of-thought, the agent deliberately picks *how* to reason, and including modules like 'consider alternative viewpoints' or 'be critical' steers it away from its single most-likely solution path. Big gains at 10-40x less compute than self-consistency, so divergence here is structural, not brute-force sampling.
- **→ Harness application.** Add a planning pre-step that, before coding/answering, picks 3-5 reasoning operators from a library (decompose, invert the problem, generate alternatives, find the counterexample, list assumptions) and writes them into an explicit PLAN structure the agent must execute. Always include at least one divergence operator ('propose two fundamentally different approaches before choosing') so the structure itself forces exploration.

#### 7. [Diversity of Thought Elicits Stronger Reasoning Capabilities in Multi-Agent Debate Frameworks](https://arxiv.org/abs/2410.12853)

- **Authors:** Mahmood Hegazy  
- **Year / venue:** 2024 · arXiv · arXiv:2410.12853  
- **Verification:** ✅ verified real — via `arxiv id_list 2410.12853` (Title and single author match exactly.)

- **Method.** Systematically varies debate composition, showing that a *heterogeneous* set of models/personas debating beats homogeneous copies of one model — e.g., diverse medium models (Gemini-Pro + Mixtral + PaLM-2-M) reach 91% on GSM-8K vs 82% for three identical Gemini-Pro instances.
- **Why it matters for divergence.** Pins down the mechanism behind why debate works: the gains come from genuine *diversity of vantage point*, not from the number of agents. Identical agents converge to a shared prior (polish); heterogeneous agents bring different priors and surface answers no single one would (novelty). Directly actionable for how to configure a debate.
- **→ Harness application.** When orchestrating debate/ensembles, maximize heterogeneity deliberately: mix models (Opus + a different provider via API), or if single-model, assign strongly distinct personas/roles (skeptic, domain expert, contrarian, first-principles physicist) and distinct tool/context budgets. Measure inter-agent answer diversity and, if it's low, perturb roles/temperature before debating — don't waste rounds on agents that already agree.

#### 8. [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073)

- **Authors:** Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, et al. (Anthropic)  
- **Year / venue:** 2022 · arXiv · arXiv:2212.08073  
- **Verification:** ✅ verified real — via `arxiv id_list 2212.08073` (Title and lead authors match exactly; full Anthropic author list confirmed.)

- **Method.** A model critiques and revises its own outputs against an explicit written set of principles (a 'constitution') to generate training data, then learns a preference model from AI-labeled comparisons (RLAIF) — self-improvement steered by externalized rules rather than per-example human labels.
- **Why it matters for divergence.** Demonstrates that a critique loop becomes principled and reliable when the critique is anchored to an *explicit external rubric* rather than the model's vibes. This is the bridge between 'self-reflection is unreliable' (Huang et al.) and useful critique: give the critic a written standard to measure against. For divergence, the 'constitution' can encode novelty/anti-conformity criteria, not just safety.
- **→ Harness application.** Give critic agents an explicit written rubric to judge against instead of open-ended 'is this good?'. For a divergence harness, write a 'novelty constitution' (e.g., 'reject the first obvious solution; require at least one non-standard approach; flag if the answer matches the most common Stack Overflow pattern') and have the critic revise the proposal until it satisfies those principles — turning vague self-critique into a checkable, divergence-promoting gate.


---

## 7. Research-idea generation & autonomous scientific discovery

<a id='7-idea-generation'></a>

*Research-idea generation & autonomous scientific discovery*

**Key takeaways**

- Over-generate-then-rank is the single most validated novelty mechanism: the Stanford 100+ researcher study (2409.04109) got expert-judged super-human novelty by sampling thousands of candidates and ranking, NOT from one strong sample. Divergence is a search/selection problem, not a single-prediction problem.
- Diversity collapses with scale unless knowledge inflow is actively managed: both the Stanford study (rising duplicate rate) and Nova (2410.14255) show that raw resampling plateaus into repetition; deliberately planning what NEW external knowledge to retrieve each round is what produced 3.4x more unique novel ideas.
- Novelty without grounding is a mirage: the Ideation-Execution Gap (2506.20803) found the LLM novelty advantage largely vanishes after 100+ hours of real execution. Any harness that diverges must re-validate ideas against feasibility/execution, not trust ideation-stage novelty scores.
- LLM self-evaluation of its own novelty is unreliable (Stanford study): the generator must not be the judge. Use a separate critic/ranker with an explicit rubric, ideally calibrated against human judgments (SciMuse 2405.17044 shows interestingness is learnable/predictable).
- Structural recombination beats free association for non-obvious ideas: SciAgents (2409.05556) and ResearchAgent (2404.07738) force connections across distant knowledge-graph nodes/entities, surfacing interdisciplinary links the LLM would never reach by following its highest-probability associations.
- Search with backtracking outperforms single-pass planning for genuine discovery: AI Scientist-v2 (2504.08066) uses agentic tree search with explicit branch evaluation and abandonment to produce a peer-review-passing paper — the agent must be willing to discard its first plan.
- Structured, multi-dimensional critique steers the novelty-validity frontier: MOOSE's past/present/future feedback (2309.02726) and ResearchAgent's role-specialized reviewers give explicit dials to avoid both 'too safe/obvious' and 'novel but invalid.'

**Harness mechanisms this theme suggests**

- Over-generate-and-rank skill: sample N candidate approaches at high temperature (each seeded by a distinct retrieval), dedup via embedding cosine, then rank with a SEPARATE novelty-only LLM judge; auto-stop when marginal unique-idea yield drops (operationalizes 2409.04109's quantity-vs-duplication finding).
- Active-retrieval diversity loop (Nova-style): before each idea batch the agent must name a knowledge gap and issue a targeted search/codebase query, conditioning the next batch only on freshly retrieved material; maintain a diversity ledger steering toward under-explored regions.
- Survives-grounding gate (Ideation-Execution Gap): no divergent idea is promoted until a cheap execution probe (failing test, tiny prototype, sanity calc) runs; re-score novelty AND feasibility post-probe and drop ideas whose appeal collapses on contact with reality.
- Random-path provocation over a concept graph (SciAgents/ResearchAgent): build a lightweight graph from repo symbols/domain/literature, sample distant node pairs, and require the agent to invent a mechanism bridging them — structurally forcing non-obvious recombination.
- Agentic tree search with an LLM-critic heuristic (AI Scientist-v2): represent approaches as a tree, expand best-first using a reviewer subagent's novelty+soundness score, and keep a backtracking stack so the agent abandons dead branches instead of committing to its first plan.
- Three-feedback self-refinement template (MOOSE): wrap drafts in past-feedback (is it obvious/known? push novelty), present-feedback (consistent with current evidence/tests? push validity), future-feedback (does it open follow-on work?), looping until both novelty and validity thresholds pass.
- Decoupled generator/judge with role-specialized reviewers (ResearchAgent): never let the generating context score itself; run N critic subagents each owning one rubric dimension (novelty, validity, clarity, feasibility) returning structured critiques the generator must resolve.
- Personalized interestingness ranker (SciMuse): condition generation on the specific user's/project's concept neighborhood and rank candidates with an LLM scorer calibrated to predict expert interest, using graph-bridging features as a selection heuristic so divergence stays targeted and relevant.

### Papers

#### 1. [Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers](https://arxiv.org/abs/2409.04109)

- **Authors:** Chenglei Si, Diyi Yang, Tatsunori Hashimoto  
- **Year / venue:** — · — · arXiv:2409.04109  
- **Verification:** ✅ verified real — via `WebFetch https://arxiv.org/abs/2409.04109` (Exact title and author list match the claim.)

- **Method.** First large-scale blind head-to-head: an LLM ideation agent (retrieval-augmented generation of many candidates, then over-generate-and-rank) vs 100+ expert NLP researchers, with ideas standardized to a template and reviewed by experts. The agent over-generates ~4000 seed ideas per topic and uses an LLM ranker to surface the top few.
- **Why it matters for divergence.** The load-bearing empirical result for divergence: LLM ideas were judged significantly MORE novel than expert ideas (p<0.05) but slightly less feasible — and critically, novelty came from massive over-generation plus ranking, not from a single sample. It also documents that the LLM lacked idea diversity (duplicate rate rose sharply with scale) and that LLM self-evaluation of novelty is unreliable. This directly motivates 'generate many, then filter' over 'predict the one best next move.'
- **→ Harness application.** Build an 'over-generate-and-rank' ideation skill: for a design/research prompt, sample N (50-100) candidate approaches at elevated temperature with a retrieval step seeding each, then run a separate LLM-judge pass that ranks ONLY on novelty/non-obviousness (never let the same context that generated an idea also score it). Track a running dedup set (embedding cosine threshold) and stop sampling when marginal new-unique-idea yield drops — operationalizing their finding that quantity plateaus into duplicates.

#### 2. [The Ideation-Execution Gap: Execution Outcomes of LLM-Generated versus Human Research Ideas](https://arxiv.org/abs/2506.20803)

- **Authors:** Chenglei Si, Tatsunori Hashimoto, Diyi Yang  
- **Year / venue:** — · — · arXiv:2506.20803  
- **Verification:** ✅ verified real — via `WebFetch https://arxiv.org/abs/2506.20803` (Exact title and author list match the claim.)

- **Method.** Follow-up execution study: 43 experts each spent 100+ hours actually implementing a randomly assigned idea (LLM- or human-authored) and wrote a short paper; the same ideas were re-reviewed post-execution.
- **Why it matters for divergence.** A crucial corrective to naive 'LLMs are more novel': the novelty advantage of LLM ideas largely evaporates after execution — LLM ideas dropped significantly more on every metric. Implication for harnesses: novelty must be validated against feasibility/execution, not just judged at the ideation stage. Divergence without a grounding/execution loop produces brilliant-sounding but brittle ideas.
- **→ Harness application.** Add a mandatory 'cheap-execution probe' stage between ideation and commitment: before a divergent idea is promoted, force a minimal runnable artifact (a failing test, a tiny prototype, a back-of-envelope calculation, a literature sanity-check) and re-score novelty AND feasibility post-probe. Penalize ideas whose appeal collapses on contact with execution — encode this as a 'survives-grounding' gate in the agent loop.

#### 3. [The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search](https://arxiv.org/abs/2504.08066)

- **Authors:** Yutaro Yamada, Robert Tjarko Lange, Cong Lu, Shengran Hu, Chris Lu, Jakob Foerster, Jeff Clune, David Ha  
- **Year / venue:** — · — · arXiv:2504.08066  
- **Verification:** ✅ verified real — via `WebFetch http://export.arxiv.org/api/query?id_list=2504.08066` (Exact title and full 8-author list match the claim.)

- **Method.** End-to-end autonomous pipeline (idea -> experiment design -> code/execute -> analyze -> write paper -> simulated review) driven by a progressive agentic tree search over experiment branches, removing the human code templates of v1 (arXiv:2408.06292). One generated manuscript passed real workshop peer review.
- **Why it matters for divergence.** Demonstrates that genuine novelty at the system level comes from SEARCH over a tree of experimental branches with explicit backtracking, not single-pass generation. The tree-search-with-evaluation loop is the concrete mechanism for exploring beyond the most-likely continuation, and the simulated-reviewer node is a self-critique signal that prunes the obvious/wrong branches.
- **→ Harness application.** Implement an agentic tree-search loop in the harness: each node = a candidate experiment/approach, expand the most-promising frontier nodes (LLM proposes children), evaluate each by actually running code, and keep an explicit backtracking stack so the agent abandons dead branches instead of committing to its first plan. Pair it with a built-in 'reviewer' subagent that scores each branch's novelty+soundness before allocating more compute — a best-first search where the heuristic is an LLM critic.

#### 4. [ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models](https://arxiv.org/abs/2404.07738)

- **Authors:** Jinheon Baek, Sujay Kumar Jauhar, Silviu Cucerzan, Sung Ju Hwang  
- **Year / venue:** — · — · arXiv:2404.07738  
- **Verification:** ✅ verified real — via `WebFetch https://arxiv.org/abs/2404.07738` (Exact title and author list match the claim.)

- **Method.** Starts from a core paper, expands context via a citation graph PLUS an entity-centric knowledge store of concepts mined across many papers, then iteratively refines the (problem, method, experiment) triple using multiple LLM ReviewingAgents whose criteria are aligned to human preferences.
- **Why it matters for divergence.** Shows two divergence levers: (1) grounding generation in an entity knowledge store forces cross-paper concept recombination rather than recall of the single most associated idea; (2) multiple specialized reviewing agents with explicit human-aligned rubrics push refinement away from the bland mean. The peer-discussion-style critique loop is what raises validity while preserving novelty.
- **→ Harness application.** Build a 'concept-recombination + multi-reviewer' skill: extract entities/concepts from the relevant codebase or literature into a scratch knowledge store, then prompt the agent to generate ideas that explicitly bridge two normally-unrelated entities. Follow with N reviewer subagents each owning ONE rubric dimension (novelty, clarity, validity, feasibility) that return structured critiques the generator must address before the idea is accepted — mimicking human peer discussion as a refinement loop.

#### 5. [SciAgents: Automating Scientific Discovery Through Multi-Agent Intelligent Graph Reasoning](https://arxiv.org/abs/2409.05556)

- **Authors:** Alireza Ghafarollahi, Markus J. Buehler  
- **Year / venue:** — · — · arXiv:2409.05556  
- **Verification:** ✅ verified real — via `WebFetch https://arxiv.org/abs/2409.05556` (Title (lowercase styling in source) and authors match the claim.)

- **Method.** Samples random paths through a large ontological knowledge graph and hands them to a role-specialized multi-agent team (Ontologist, Scientist, Critic, etc.) that turns the path into a hypothesis, mechanism, and design, with in-situ learning and tool/data retrieval.
- **Why it matters for divergence.** Its core novelty engine is sampling RANDOM walks/paths across a knowledge graph to force connections between concepts 'previously considered unrelated' — a structural antidote to the LLM defaulting to the highest-probability association. The Ontologist-defines-then-Scientist-connects division shows how separating concept-grounding from idea-synthesis surfaces interdisciplinary, non-obvious links.
- **→ Harness application.** Add a 'random-path provocation' mechanism: build a lightweight concept graph (from the codebase symbols, the domain, or retrieved literature), then sample random pairs/triples of distant nodes and require the agent to invent a plausible mechanism connecting them. Use distinct subagent roles — one that only structures/defines concepts, one that only proposes the bridging idea, one adversarial critic — so the divergence step is structurally insulated from premature convergence.

#### 6. [Nova: An Iterative Planning and Search Approach to Enhance Novelty and Diversity of LLM Generated Ideas](https://arxiv.org/abs/2410.14255)

- **Authors:** Xiang Hu, Hongyu Fu, Jinge Wang, Yifeng Wang, Zhikun Li, Renjun Xu, Yu Lu, Yaochu Jin, Lili Pan, Zhenzhong Lan  
- **Year / venue:** — · — · arXiv:2410.14255  
- **Verification:** ✅ verified real — via `WebFetch https://arxiv.org/abs/2410.14255` (Exact title and full 10-author list match the claim.)

- **Method.** Each generation cycle the LLM plans a FOCUSED external-knowledge retrieval query (theories, prior discoveries), ingests the results, and progressively enriches/diversifies the idea pool; iterating the plan-retrieve-generate loop compounds breadth and depth.
- **Why it matters for divergence.** Directly attacks the 'simplistic and repetitive' failure mode: by making the agent deliberately plan WHAT new external knowledge to fetch each round, it increased unique novel ideas 3.4x over baseline. This is the cleanest demonstration that diversity is bottlenecked by knowledge inflow, not sampling temperature — divergence is an information-acquisition problem.
- **→ Harness application.** Encode an 'active-retrieval planning' loop: before each new idea batch, the agent must articulate what knowledge gap to fill and issue a targeted search/web/codebase query, then condition the next generation on the new material — never generate two batches from the same context. Maintain a diversity ledger and explicitly steer each round toward under-explored regions, turning ideation into iterative knowledge expansion rather than re-sampling the same prior.

#### 7. [Large Language Models for Automated Open-domain Scientific Hypotheses Discovery (MOOSE)](https://arxiv.org/abs/2309.02726)

- **Authors:** Zonglin Yang, Xinya Du, Junxian Li, Jie Zheng, Soujanya Poria, Erik Cambria  
- **Year / venue:** — · — · arXiv:2309.02726  
- **Verification:** ✅ verified real — via `WebFetch https://arxiv.org/abs/2309.02726` (Title and author list match the claim; MOOSE is the framework name from the paper.)

- **Method.** Defines open-domain hypothetical induction from raw web corpora and proposes a multi-module framework with three explicit feedback mechanisms — past-feedback, present-feedback, and future-feedback — to iteratively push hypotheses toward being both novel ('not in the literature') and valid ('reflecting reality').
- **Why it matters for divergence.** Provides a concrete, reusable critique-feedback taxonomy for steering generation along the novelty-validity frontier rather than collapsing to safe restatements. The temporal feedback framing (what's been tried / current evidence / future implications) is a structured prompt schema that demonstrably yields PhD-judged novel-and-valid hypotheses.
- **→ Harness application.** Adopt the three-feedback schema as a reusable self-refinement prompt template: after a draft idea, run a past-feedback pass (is this already known / obvious? — push for novelty), a present-feedback pass (is it consistent with current evidence/tests? — push for validity), and a future-feedback pass (does it open follow-on work?). Loop until both novelty and validity thresholds are met, giving the agent an explicit dial between 'too safe' and 'unmoored.'

#### 8. [Interesting Scientific Idea Generation Using Knowledge Graphs and LLMs: Evaluations with 100 Research Group Leaders (SciMuse)](https://arxiv.org/abs/2405.17044)

- **Authors:** Xuemei Gu, Mario Krenn  
- **Year / venue:** — · — · arXiv:2405.17044  
- **Verification:** ✅ verified real — via `WebFetch https://arxiv.org/abs/2405.17044` (Title and authors match the claim; SciMuse is the system name from the paper.)

- **Method.** Builds an evolving knowledge graph from 58M papers, generates personalized ideas via GPT-4 conditioned on graph neighborhoods, and has 100+ Max Planck research-group leaders rank 4,400+ ideas by interest; then trains supervised predictors and zero-shot LLM rankers of 'interestingness.'
- **Why it matters for divergence.** Largest expert-grounded study tying idea quality to measurable knowledge-graph properties, showing interest-level can be predicted and OPTIMIZED. It establishes that personalization (conditioning on the recipient's own concept neighborhood) and graph structure are controllable knobs for surfacing ideas an expert finds genuinely compelling — divergence that is targeted, not random.
- **→ Harness application.** Add a learned/zero-shot 'interestingness ranker' as a filter stage and personalize generation: condition idea proposals on the specific user's/project's concept neighborhood (their recent work, the repo's domain graph) and rank candidates with an LLM scorer calibrated to predict expert interest.


---

## 8. Analogical, lateral & conceptual-blending reasoning

<a id='8-analogy-lateral'></a>

*Analogical, lateral & conceptual-blending reasoning*

**Key takeaways**

- Divergence is a two-phase move, not one prompt: first lift the problem OUT of its surface form (step-back abstraction, structured/schema representation), then transfer or recombine at that higher level, then descend back to a concrete, coherent answer. Token-level continuation is precisely what anchors a model to the obvious; the structured/abstract layer is where non-obvious combinations become reachable.
- Self-generated analogs beat fixed exemplars: making the model recall and solve its OWN analogous problems (Analogical Prompting, Thought Propagation) conditions the answer on relational structure rather than the most-likely next token — and solving the analogs FIRST prevents premature convergence on the target's greedy path.
- Semantic distance is the tunable diversity knob (Serendipity by Design): the creative payoff of a cross-domain seed grows the more remote the source is. Random nearby seeds barely help; deliberately MAXIMALLY-distant seeds with an enforced mapping do.
- Cross-domain prompts help LLMs less than humans by default — the model needs the mapping FORCED and the source DISTANT, otherwise it collapses back to in-distribution ideas. Optionality kills it; the transfer must be a required, cited step.
- Conceptual blending needs an explicit bridge: novelty-that-is-grounded comes from finding the connecting concept between two input spaces (PopBlends) and recombining structured slots (Cooking Up Creativity), not from blending raw text.
- Lateral thinking is elicited by interactive hypothesis-probing under incomplete information (Weak-eval-Strong): forcing the model to ask falsifying questions before answering surfaces alternatives a one-shot completion skips.
- You must measure divergence to trust it: originality/flexibility/fluency gated by feasibility/clarity (LiveIdeaBench) distinguishes 'genuinely novel and usable' from 'merely different,' and watch for flexibility-collapse / homogenization as the failure mode of LLM-assisted ideation.

**Harness mechanisms this theme suggests**

- Mandatory step-back gate: block concrete edits/answers until the agent records (a) the abstract problem class, (b) 2-3 principle-level solution families for that class. Forces breadth before the first commit (from Take a Step Back).
- Analogize-first pre-step: require the agent to self-generate N structurally-analogous problems from DIFFERENT domains, state each one's core trick, then implement by explicitly mapping the chosen trick and citing it (from Analogical Reasoners + Thought Propagation).
- Distant-seed injector: maintain an embedded corpus of domains/objects; each ideation round, sample the source MAXIMALLY far from the task domain and require a property-mapping from it. Expose semantic distance as a CLI dial and auto-escalate distance until coherence breaks (from Serendipity by Design).
- Schema crossover engine: decompose every candidate into slots (goal/mechanism/constraint/medium/failure-mode), swap slots across semantically distant candidates, back-translate the recombined schema to a concrete proposal. A genetic-style recombination over structured representations (from Cooking Up Creativity).
- Blend skill: given task domain + a forced unrelated domain, run PopBlends stages (attributes of each space -> bridging concept -> blended artifact -> coherence prune) to import a foreign mechanism into the solution (from PopBlends).
- Falsify-your-first-answer loop: before committing, the agent must ask 5 questions that would rule out its initial/obvious interpretation, answered by a judge subagent holding hidden spec details (from Weak-eval-Strong).
- Diverge-then-converge with a creativity judge: generate a wide candidate set, score each on originality/flexibility/feasibility/clarity, keep the Pareto front (high originality AND feasibility), and reject if the set collapses into one category (homogenization detector) (from LiveIdeaBench).
- Parallel-analog fan-out: spawn k subagents each solving a deliberately different analog of the task, then a synthesis agent must inherit at least one non-obvious move from each analog into the final design (from Thought Propagation).

### Papers

#### 1. [Large Language Models as Analogical Reasoners](https://arxiv.org/abs/2310.01714)

- **Authors:** Michihiro Yasunaga, Xinyun Chen, Yujia Li, Panupong Pasupat, Jure Leskovec, Percy Liang, Ed H. Chi, Denny Zhou  
- **Year / venue:** — · — · arXiv:2310.01714  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2310.01714` (Title and 8-author list match exactly; ICLR 2024.)

- **Method.** Analogical Prompting: instead of supplying fixed exemplars, the model is told to self-generate relevant exemplars/knowledge ('recall a few related problems and how you solved them') before solving the target problem, then solve by analogy to its own recalled cases.
- **Why it matters for divergence.** Directly counters in-distribution continuation by making the model first surface and articulate analogous prior structures, so the eventual answer is conditioned on retrieved relational patterns rather than on the single most-likely surface continuation. It externalizes the 'what is this like?' step that humans use to escape fixation.
- **→ Harness application.** Add an 'analogize-first' pre-step to the agent loop: before writing code or a design, force a turn that emits 3-5 self-generated analogous problems from DIFFERENT subsystems/domains plus the abstract solution schema each used, then require the implementation to cite which recalled schema it is transferring. Encode as a skill that injects 'Recall N structurally-analogous problems you have solved (vary the domain each time), state each one's core trick, then solve THIS by mapping the best trick.'

#### 2. [Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models](https://arxiv.org/abs/2310.06117)

- **Authors:** Huaixiu Steven Zheng, Swaroop Mishra, Xinyun Chen, Heng-Tze Cheng, Ed H. Chi, Quoc V. Le, Denny Zhou  
- **Year / venue:** — · — · arXiv:2310.06117  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2310.06117` (Title and authors match exactly; ICLR 2024.)

- **Method.** Step-Back Prompting: prompt the model to first abstract a specific question into a higher-level concept or first-principle ('what is the general principle behind this?'), retrieve/reason about that abstraction, then descend back to the concrete instance to answer.
- **Why it matters for divergence.** Moving up an abstraction level is the prerequisite for lateral transfer: at the abstract layer, solutions from far-away domains become reachable because surface details (which anchor the model to the obvious continuation) are stripped away. It widens the candidate space before committing.
- **→ Harness application.** Insert a mandatory 'step-back' node before solution generation: the agent must state the governing principle / problem class (e.g., 'this is a cache-invalidation problem', 'this is a consensus problem') and list how that class is solved generally, THEN specialize. Build as a /step-back skill that blocks concrete edits until an abstraction statement and 2-3 principle-level options are recorded, forcing breadth before depth.

#### 3. [Thought Propagation: An Analogical Approach to Complex Reasoning with Large Language Models](https://arxiv.org/abs/2310.03965)

- **Authors:** Junchi Yu, Ran He, Rex Ying  
- **Year / venue:** — · — · arXiv:2310.03965  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2310.03965` (Title and authors match exactly; ICLR 2024.)

- **Method.** Thought Propagation (TP): the model proposes a set of analogous problems, solves them first, then either reuses those solutions directly or aggregates them into a plan to produce/amend the target solution — propagating insight from analogs rather than reasoning the target from scratch.
- **Why it matters for divergence.** Forces exploration of a neighborhood of related problems and then recombines their solutions, so novelty emerges from cross-pollination of multiple analogs instead of a single greedy chain. The explicit 'solve the analogs first' step prevents premature convergence on the target's obvious path.
- **→ Harness application.** Implement a fan-out subagent pattern: spawn k parallel subagents each solving a deliberately analogous-but-different version of the task (different stack, different scale, different constraint), then a synthesis agent aggregates/maps their solutions onto the real task and amends. Encode the aggregation rule: 'the final design must inherit at least one non-obvious move from each analog solution.'

#### 4. [Cooking Up Creativity: Enhancing LLM Creativity through Structured Recombination](https://arxiv.org/abs/2504.20643)

- **Authors:** Moran Mizrahi, Chen Shani, Gabriel Stanovsky, Dan Jurafsky, Dafna Shahaf  
- **Year / venue:** — · — · arXiv:2504.20643  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2504.20643` (Title and authors match exactly; accepted at TACL.)

- **Method.** Translate ideas from natural language into an explicit STRUCTURED representation, apply cognitively-inspired manipulations/recombinations on that structure (not on tokens), then translate back to natural language. Demonstrated via DishCOVER for novel recipe generation; beats GPT-4o on novelty and diversity while staying coherent.
- **Why it matters for divergence.** Token-level generation is exactly what pulls a model toward the most-likely continuation; lifting ideas into a structured/schematic space and recombining there is what produces combinations the surface distribution would never reach, while the back-translation keeps them coherent and feasible.
- **→ Harness application.** For ideation tasks, add a 'decompose-to-schema then recombine' phase: have the agent extract each candidate into slots (goal, mechanism, constraint, material/medium, failure-mode), then systematically swap slots across candidates (crossover) and back-translate the recombined schema into a concrete proposal. A skill maintains a small library of schemas mined from prior solutions and explicitly mixes slots from semantically distant entries.

#### 5. [PopBlends: Strategies for Conceptual Blending with Large Language Models](https://arxiv.org/abs/2111.04920)

- **Authors:** Sitong Wang, Savvas Petridis, Taeahn Kwon, Xiaojuan Ma, Lydia B. Chilton  
- **Year / venue:** — · — · arXiv:2111.04920  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2111.04920` (Title and authors match exactly; CHI 2023 (arXiv v3 Feb 2023).)

- **Method.** An automated pipeline for conceptual blending: given a user topic and a target (pop-culture) domain, it combines traditional knowledge extraction with LLM prompting to find a connecting concept that bridges the two input spaces, generating blend suggestions; users found ~2x more blends at half the mental demand.
- **Why it matters for divergence.** Operationalizes Fauconnier-Turner conceptual blending — finding the shared/bridging concept between two distant input spaces is the core mechanic of producing a genuinely novel-yet-grounded third idea, rather than continuing either input space alone.
- **→ Harness application.** Build a 'blend' skill that takes the problem domain plus a deliberately unrelated second domain (user-supplied or randomly drawn) and runs PopBlends-style stages: (1) list salient attributes of each space, (2) find bridging concepts where attributes align, (3) generate the blended artifact, (4) prune for coherence. Use it to force a coding agent to import a mechanism from a foreign domain (e.g., 'blend rate-limiter with traffic-light semantics').

#### 6. [Weak-eval-Strong: Evaluating and Eliciting Lateral Thinking of LLMs with Situation Puzzles](https://arxiv.org/abs/2410.06733)

- **Authors:** Qi Chen, Bowen Zhang, Gang Wang, Qi Wu  
- **Year / venue:** — · — · arXiv:2410.06733  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2410.06733` (Title and authors match exactly; NeurIPS 2024.)

- **Method.** Introduces SPLAT (975 situation puzzles) and a multi-turn player-judge self-play framework: the player LLM must ask probing questions to deduce a hidden scenario from incomplete information while a judge answers; the iterative questioning elicits lateral (out-of-the-box) reasoning and transfers to other reasoning benchmarks.
- **Why it matters for divergence.** Lateral thinking under incomplete information is the antidote to confident in-distribution completion. The interactive question-asking loop forces the model to generate non-obvious hypotheses and test them, surfacing alternatives it would otherwise skip when answering in one shot.
- **→ Harness application.** Wrap ambiguous tasks in a player-judge loop: before committing, the agent must ask itself (or a judge subagent holding hidden spec details) a series of hypothesis-probing questions that each rule out an obvious interpretation, only acting once the obvious reading has been actively challenged. Encode 'ask 5 questions that would falsify your first interpretation' as a guard step.

#### 7. [Serendipity by Design: Evaluating the Impact of Cross-domain Mappings on Human and LLM Creativity](https://arxiv.org/abs/2603.19087)

- **Authors:** Qiawen Ella Liu, Marina Dubova, Henry Conklin, Takumi Harada, Thomas L. Griffiths  
- **Year / venue:** — · — · arXiv:2603.19087  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2603.19087` (Title and authors match exactly; cs.AI/cs.CL, submitted March 2026.)

- **Method.** Empirically compares forced cross-domain mapping (translate a property from a RANDOMLY assigned remote source domain, e.g. octopus/cactus/GPS) against need-driven ideation, for both humans and LLMs. Finding: the creativity benefit of a cross-domain prompt grows as the inspiration source becomes more semantically DISTANT from the target.
- **Why it matters for divergence.** Gives a tunable knob for divergence: novelty scales with the semantic distance of the injected source. It shows random remote seeds are a reliable lever and warns that naive cross-domain prompts help LLMs less than humans on average — so the seed must be deliberately distant and the mapping enforced, not optional.
- **→ Harness application.** Add a 'distant-seed injection' mechanism: maintain a corpus of domains/objects with embeddings, and for each ideation round sample a source MAXIMALLY far (by embedding distance) from the task domain, then require the agent to map a property of that source onto the solution. Sweep distance as a diversity dial and keep the most distant seeds that still yield coherent mappings.

#### 8. [LiveIdeaBench: Evaluating LLMs' Divergent Thinking for Scientific Idea Generation with Minimal Context](https://arxiv.org/abs/2412.17596)

- **Authors:** Kai Ruan, Xuan Wang, Jixiang Hong, Peng Wang, Yang Liu, Hao Sun  
- **Year / venue:** — · — · arXiv:2412.17596  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2412.17596` (Verified; arxiv title includes 'Capabilities' ('...Divergent Thinking Capabilities for...') — semantically identical, minor wording difference from candidate. Authors match exactly.)

- **Method.** A self-updating benchmark that probes divergent thinking from single-keyword prompts across 1,180 keywords / 22 scientific domains and 40+ models, scoring on five Guilford-grounded dimensions: originality, feasibility, fluency, flexibility, clarity. Finds idea-generation ability is poorly predicted by general-intelligence metrics.
- **Why it matters for divergence.** Provides the measurement rubric for whether a harness actually diverged: fluency (how many ideas), flexibility (how many distinct categories), originality (distance from typical), gated by feasibility and clarity. It separates 'genuinely novel and usable' from 'merely different,' which is exactly the convergent check a divergence loop needs.
- **→ Harness application.** Use the five dimensions as an automated judge inside a generate-then-filter loop: after divergent generation, an LLM-judge scores each candidate on originality/flexibility/feasibility/clarity and the loop keeps the Pareto-front (high originality AND feasibility), penalizing flexibility collapse (too many ideas in one category). Bake the rubric into a /score-ideas skill that also tracks effective number of distinct categories to detect homogenization.


---

## 9. Measuring creativity, novelty, surprise & diversity in LLM output

<a id='9-creativity-eval'></a>

*Measuring creativity, novelty, surprise & diversity in LLM output*

**Key takeaways**

- Creativity must be measured as novelty AND quality jointly (Padmakumar's harmonic-mean frontier; NoveltyBench's quality-weighted utility_k). Optimizing originality alone is trivially gamed by producing bad or random output, so any harness reward must gate originality on a quality check.
- Diversity needs functional equivalence classes, not surface metrics. NoveltyBench shows the right unit is 'does this response add distinct value', detected by a trained pairwise classifier / LLM-judge, not distinct-n or self-BLEU which only catch lexical variation.
- Mode collapse is largely an inference-time, fixable problem. Verbalized Sampling recovers 1.6-2.1x diversity with zero training by making the model verbalize a probability distribution and surface its tail; explicitly steering toward low-probability-but-valid branches is the lever.
- Constraint accumulation forces genuine divergence. Denial Prompting (NeoGauge) — iteratively banning the strategy just used — reliably drives an agent into fresh regions of solution space and yields a measurable count of distinct valid strategies.
- Reference-free spread scores are cheap and useful. DAT-style mean pairwise semantic distance is an automatable fitness function for divergent thinking, with sampling/temperature as a direct creativity knob (with a creativity-vs-stability trade-off).
- Calibrated LLM-judges beat raw embedding distance for human-perceived originality (Ocsai: r≈0.78 vs ≈0.19), but judges are prompt-sensitive and label-biased (Rethinking Creativity Evaluation), so they must be anchored with human-rated exemplars and periodically recalibrated.
- No single creativity metric generalizes across domains and metrics often disagree — credible proof of 'more creative' requires a multi-metric ensemble plus periodic human calibration, and metric disagreement should itself be treated as a gaming/overfitting alarm.

**Harness mechanisms this theme suggests**

- Verbalized-sampling front door: every ideation/brainstorm skill first asks the model for N candidates WITH self-assigned probabilities, then deliberately advances candidates from the low-probability-but-still-valid tail instead of the argmax; expose the probability floor as a tunable creativity dial.
- Functional-dedup loop (NoveltyBench utility_k): generate k candidates, cluster into equivalence classes via embedding-threshold or an 'are these functionally the same?' LLM-judge, drop duplicates, and keep sampling until distinct_k plateaus; rank surviving ideas by patience-discounted cumulative utility.
- Denial loop (NeoGauge): after each solution, auto-extract its core strategy, re-prompt 'solve this WITHOUT that approach', iterate until valid moves exhaust; collect all distinct valid solutions and score them against a corpus of prior/known answers to certify off-the-beaten-path novelty.
- Originality-quality frontier selector: score every candidate on originality (n-gram/embedding distance from references or the agent's own prior outputs) and quality (LLM-judge/task metric), select by their harmonic mean, and reject any candidate that buys originality by losing quality.
- DAT spread gate: embed the key concepts of a brainstormed set and compute mean pairwise cosine distance; block shipping idea sets that are too semantically clustered and use the spread score to choose which subset to expand.
- Calibrated originality judge (Ocsai-style): use a few-shot LLM-judge anchored with human-rated high/low-originality exemplars as the reward model in best-of-k/rejection sampling, with periodic human spot-checks to detect judge drift.
- Multi-metric creativity dashboard: track spread score + distinct-class count + calibrated judge originality + originality/quality harmonic mean per run; require cross-metric agreement before claiming a creativity win, and surface metric disagreement as a single-metric-gaming alarm — this is how you PROVE the intervention worked rather than overfit one number.
- Creativity regression harness: store baseline metric distributions and A/B every prompt/skill change against them so any 'make it more divergent' edit must demonstrably push diversity/novelty up without dropping quality, just as code changes pass tests.

### Papers

#### 1. [NoveltyBench: Evaluating Language Models for Humanlike Diversity](https://arxiv.org/abs/2504.05228)

- **Authors:** Yiming Zhang, Harshita Diddee, Susan Holm, Hanchen Liu, Xinyue Liu, Vinay Samuel, Barry Wang, Daphne Ippolito  
- **Year / venue:** 2025 · arXiv (CMU); COLM-adjacent · arXiv:2504.05228  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2504.05228` (Exact title and full author list match the arxiv abstract page.)

- **Method.** A benchmark that elicits many generations per prompt, partitions them into functional-equivalence classes via a DeBERTa classifier trained on 1,100 human-annotated generation pairs, scores each generation's quality with a reward model (Skywork-Reward-Gemma, 1-10), then combines them into distinct_k (count of unique equivalence classes) and a patience-discounted cumulative-utility score utility_k = [(1-p)/(1-p^k)]·Σ p^(i-1)·[c_i is new]·u_i with p=0.8.
- **Why it matters for divergence.** Gives a concrete, automatable objective that rewards an agent for producing genuinely DIFFERENT high-quality answers rather than k paraphrases of the single most-likely answer. The equivalence-class partition is exactly the signal needed to detect when an agent has collapsed onto one idea, and the discounted-utility score lets a harness prove diversity gains numerically.
- **→ Harness application.** Bake utility_k into a self-scoring loop: have the agent emit k candidate solutions, run a cheap equivalence-class clustering (embedding + threshold, or an LLM-judge 'are these functionally the same?' prompt mirroring their DeBERTa pairwise labels), discard duplicates, and only keep generating until distinct_k stops increasing. Use the patience-discounted score as a reward signal for best-of-k selection and as a regression test ('did this skill raise distinct_k vs baseline?').

#### 2. [Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity](https://arxiv.org/abs/2510.01171)

- **Authors:** Jiayi Zhang, Simon Yu, Derek Chong, Anthony Sicilia, Michael R. Tomz, Christopher D. Manning, Weiyan Shi  
- **Year / venue:** 2025 · arXiv (Stanford/Northeastern) · arXiv:2510.01171  
- **Verification:** ✅ verified real — via `WebFetch arxiv export API id_list=2510.01171` (Exact title and full author list match the arxiv feed.)

- **Method.** Identifies 'typicality bias' in preference data as the root cause of RLHF mode collapse, then proposes a training-free prompt: instruct the model to verbalize a distribution over multiple responses with explicit probabilities (e.g. 'Generate 5 jokes and their probabilities'), surfacing the tail of the distribution. Reports 1.6-2.1x diversity gains over direct prompting while preserving quality/safety, with larger models benefiting more.
- **Why it matters for divergence.** Directly converts a next-token predictor into a distribution sampler at inference time. By forcing the model to name lower-probability modes and assign them probabilities, it makes the agent explicitly reason about alternatives it would otherwise never surface, and the probabilities give a built-in surprise/rarity signal to prefer the unlikely-but-valid branch.
- **→ Harness application.** Add a 'verbalized sampling' step at the front of any ideation skill: prompt for N candidates WITH self-assigned probabilities, then deliberately advance the LOW-probability, high-plausibility candidates (e.g. pick from the bottom tercile that still pass a validity check) instead of the argmax. Tune the probability-floor as a creativity dial. Zero training cost, drop-in for Claude Code/Codex.

#### 3. [Probing the Creativity of Large Language Models: Can Models Produce Divergent Semantic Association?](https://arxiv.org/abs/2310.11158)

- **Authors:** Honghua Chen, Nai Ding  
- **Year / venue:** 2023 · EMNLP 2023 Findings · arXiv:2310.11158  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2310.11158` (Title (case variation only) and both authors match the arxiv abstract page.)

- **Method.** Adapts the Divergent Association Task (DAT) to LLMs: ask the model to produce mutually unrelated words and score creativity as the mean pairwise semantic distance (embedding cosine distance) between them. Tests greedy vs temperature vs stochastic sampling, finding sampling/temperature raise DAT scores (with a creativity-vs-stability trade-off) for all models except GPT-4, which already scores highly under greedy.
- **Why it matters for divergence.** Provides an objective, reference-free, model-internal proxy for divergent thinking that needs no human raters. Mean semantic distance is a cheap fitness function a harness can compute on the fly to reward an agent for spreading out across concept space instead of clustering near one obvious region.
- **→ Harness application.** Implement a DAT-style 'spread score': embed an agent's candidate ideas (or the key noun phrases of each) and compute mean pairwise cosine distance; use it as a quantitative diversity gate that blocks shipping a set of ideas that are all semantically clustered, and as the selection criterion when choosing which subset of brainstormed options to expand. Also expose temperature/sampling as an explicit creativity knob per their findings.

#### 4. [Benchmarking Language Model Creativity: A Case Study on Code Generation (NeoGauge / Denial Prompting / NeoCoder)](https://arxiv.org/abs/2407.09007)

- **Authors:** Yining Lu, Dixuan Wang, Tianjian Li, Dongwei Jiang, Sanjeev Khudanpur, Meng Jiang, Daniel Khashabi  
- **Year / venue:** 2025 · NAACL 2025 · arXiv:2407.09007  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2407.09007` (Base title and full author list match; the parenthetical NeoGauge/Denial Prompting/NeoCoder are the paper's named contributions, not part of the arxiv title.)

- **Method.** Operationalizes creativity as convergent thinking (solving the goal) PLUS divergent thinking (finding qualitatively new strategies). Introduces 'Denial Prompting': iteratively forbid the strategy the model just used, forcing a genuinely different solution each round; and NeoGauge, a metric scoring both how many distinct valid strategies a model discovers and whether they differ from prior human solutions, evaluated on Codeforces (NeoCoder dataset).
- **Why it matters for divergence.** The constraint-accumulation loop is a direct recipe for pushing an agent off its default answer: each iteration bans the obvious move, so the agent must search a fresh region of the solution space. NeoGauge gives a way to measure whether the new solutions are actually novel relative to a corpus of prior answers, not just superficially different.
- **→ Harness application.** Build a 'denial loop' skill: after the agent proposes a solution, automatically extract its core strategy/approach, append a constraint 'now solve it WITHOUT using <that approach>', and repeat until constraints exhaust valid moves. Keep every distinct valid solution, then score the set against known/prior solutions (NeoGauge-style) to certify the agent found something off the beaten path. Strong fit for code, design, and algorithm tasks.

#### 5. [Beyond Semantic Distance: Automated Scoring of Divergent Thinking Greatly Improves with Large Language Models (Ocsai)](https://www.sciencedirect.com/science/article/abs/pii/S1871187123001256)

- **Authors:** Peter Organisciak, Selcuk Acar, Denis Dumas, Kelly Berthiaume  
- **Year / venue:** 2023 · Thinking Skills and Creativity (Elsevier) · Thinking Skills and Creativity (Elsevier)  
- **Verification:** ✅ verified real — via `WebFetch Crossref API (DOI 10.1016/j.tsc.2023.101356)` (No arxiv ID; confirmed via Crossref. Exact title, all four authors, journal (Thinking Skills and Creativity vol 49) and 2023 year match.)

- **Method.** Fine-tunes LLMs (the 'Ocsai' models) on thousands of human-judged Alternate Uses Task responses to predict originality scores, achieving r≈0.78 correlation with human raters versus r≈0.19 for prior pure semantic-distance methods, and shows few-shot GPT-3/3.5/4 already beat semantic-distance baselines.
- **Why it matters for divergence.** Demonstrates that an LLM-as-judge, properly grounded in human originality ratings, is a far more reliable creativity meter than embedding distance alone. This is the validated scoring head a harness needs to optimize for human-perceived originality rather than mere lexical/semantic difference, which can be gamed.
- **→ Harness application.** Use a calibrated LLM-judge originality scorer (few-shot with human-anchored examples, Ocsai-style) as the reward model inside a best-of-k or rejection-sampling loop, instead of raw embedding distance. Anchor the judge with a rubric and exemplar high/low-originality responses so scores stay stable; periodically spot-check against human ratings to keep the judge calibrated and detect drift.

#### 6. [Measuring LLM Novelty as the Frontier of Original and High-Quality Output](https://arxiv.org/abs/2504.09389)

- **Authors:** Vishakh Padmakumar, Chen Yueh-Han, Jane Pan, Valerie Chen, He He  
- **Year / venue:** 2025 · arXiv (NYU/CMU) · arXiv:2504.09389  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2504.09389` (Title (case variation only) and full author list match the arxiv abstract page.)

- **Method.** Defines novelty as the harmonic mean of (fraction of n-grams unseen during training) and a task-specific quality score, so an output only counts as novel if it is BOTH original relative to the training/reference corpus AND high quality. Evaluated across OLMo/OLMo-2/Pythia, showing scale and post-training raise novelty via quality, while naive prompting boosts originality only by sacrificing quality.
- **Why it matters for divergence.** Solves the central failure mode of optimizing creativity: an agent can trivially be 'original' by being bad or random. Pinning novelty to the Pareto frontier of original-AND-good is exactly the objective a harness should optimize so it doesn't reward garbage, and it warns that prompt-only diversity tricks often trade away quality.
- **→ Harness application.** Score candidate outputs on two axes — originality (n-gram/embedding distance from a reference set or the agent's own prior answers) and quality (LLM-judge or task metric) — and select by their harmonic mean, never by originality alone. Plot the originality-quality frontier across runs to PROVE a creativity intervention pushed the frontier outward rather than just adding noise; reject any candidate that gains originality by losing quality.

#### 7. [Rethinking Creativity Evaluation: A Critical Analysis of Existing Creativity Evaluations](https://arxiv.org/abs/2508.05470)

- **Authors:** Li-Chun Lu, Miri Liu, Pin-Chun Lu, Yufei Tian, Shao-Hua Sun, Nanyun Peng  
- **Year / venue:** 2026 · EACL 2026 · arXiv:2508.05470  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2508.05470` (Exact title and full author list match the arxiv abstract page.)

- **Method.** Systematically stress-tests four popular creativity metrics (perplexity, LLM-as-a-Judge, Creativity Index, syntactic templates) across creative writing, problem-solving, and research ideation, showing each captures something different and they frequently disagree on the same outputs; perplexity tracks fluency not novelty, LLM-judges are prompt-sensitive and label-biased, and Creativity Index is lexical-diversity-bound and fails outside writing.
- **Why it matters for divergence.** This is the meta-warning for anyone building a creativity-optimizing harness: optimizing a single metric will overfit it and not generalize. It argues for multi-metric, domain-aware measurement aligned to human judgment, which is essential to credibly PROVE an agent got more creative rather than just hacking one number.
- **→ Harness application.** Never optimize one creativity score. Build a metric ensemble (semantic-distance spread + distinct-class count + calibrated LLM-judge originality + originality/quality harmonic mean) and require AGREEMENT or report each separately per domain; treat large metric disagreement as a flag that the agent may be gaming a single metric. Add a periodic human-rating calibration check so the harness's creativity claims stay honest.


---

## 10. Exploration, curiosity & intrinsic motivation for reasoning agents

<a id='10-rl-exploration'></a>

*Exploration, curiosity & intrinsic motivation for reasoning agents*

**Key takeaways**

- Reward-maximizing fine-tuning systematically NARROWS, not widens, the reachable solution set: RLVR boosts pass@1 but base models match/beat it at large pass@k (2504.13837). The default failure mode of a trained agent is confident tunnel vision, so divergence must be engineered against the grain of the objective.
- Entropy collapse has a mechanistic cause — the positive covariance between token probability and advantage means already-confident, high-reward tokens get reinforced hardest and choke exploration (2505.22617). Collapse is predictable and can be counteracted at specific 'fork' tokens rather than globally.
- High entropy/uncertainty is signal, not noise: uncertain tokens coincide with pivotal logical branches, self-verification, and rare behaviors (2506.14758). The right policy is to LEAN INTO uncertainty at decision points, not smooth it away.
- Measuring and rewarding the SET of attempts (pass@k) instead of the single best (pass@1) dissolves the false exploration/exploitation conflict — they can mutually reinforce (2508.10751). Optimize portfolios of approaches, not one confident answer.
- An agent can self-detect under-exploration with cheap intrinsic signals it computes about itself: own-output overconfidence/perplexity, and disagreement (variance) across multiple critic/value estimates (2509.09675). These give a principled 'when to explore more' trigger.
- Diversity must be made an explicit reward, not hoped for: scoring candidates by how semantically DIFFERENT their reasoning is from siblings (EVOL-RL, 2509.15194) is the core anti-collapse pressure, even label-free, and is a direct evolutionary selection+variation analogue.
- Naive parallel multi-sampling re-draws the dominant mode; SEQUENTIAL generation conditioned on prior samples ('be different from what you already produced') is a retrain-free decoding/agent-loop trick that actually achieves coverage (2510.15502).

**Harness mechanisms this theme suggests**

- Coverage-budget skill (pass@k loop): for any non-trivial task, require N genuinely distinct candidate plans/solutions before committing; score the harness on best-of-N against tests/verifier, not on the first answer. Adaptively raise N for subtasks flagged as hard or uncertain.
- Diversity-conditioned sequential brainstorming (SESA-style): generate plan sketches one at a time, each prompt explicitly fed all prior sketches with an instruction to take a meaningfully non-overlapping approach; embed-and-deduplicate to reject near-clones, then expand only the most distinct/promising sketches into code.
- Explicit novelty reward (EVOL-RL-style selection+variation): keep a consensus answer as a stability anchor but actively favor the candidate whose reasoning is most semantically distant from the rest; maintain a persistent 'population' of approaches across iterations and penalize regression to a single mode.
- Curiosity gate (CDE-style intrinsic trigger): compute self-confidence/perplexity on the agent's own answer and run an ensemble of lightweight critic prompts; when confidence is suspiciously high OR critics disagree (high variance), spend extra exploration budget and force an alternative line of attack.
- Fork-token re-sampling (entropy-mechanism-style): detect pivotal decision points (which algorithm/file/hypothesis) and deliberately re-sample alternatives there instead of accepting the greedy choice — protect high-leverage forks from premature commitment, mirroring Clip-Cov/KL-Cov's selective protection of high-covariance tokens.
- Lean-into-uncertainty beat: at the agent's most uncertain reasoning steps, mandatorily insert a 'what else could this be?' branch-and-self-verify step and reward deeper reasoning there, converting uncertainty into exploration rather than glossing it over.
- Collapse monitor: track inter-candidate agreement / output entropy across a session as a live proxy for the policy narrowing; when agreement rises past a threshold (exploration vanishing), automatically inject a counter-pressure divergent branch before any final commitment.
- Pass@k-not-pass@1 evaluation harness: judge divergence quality by the union/coverage of distinct correct approaches across attempts (large-k mindset) so the agent is explicitly credited for reaching solutions outside its single argmax move.

### Papers

#### 1. [Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?](https://arxiv.org/abs/2504.13837)

- **Authors:** Yang Yue, Zhiqi Chen, Rui Lu, Andrew Zhao, Zhaokai Wang, Yang Yue, Shiji Song, Gao Huang  
- **Year / venue:** 2025 · NeurIPS · arXiv:2504.13837  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2504.13837` (Title and full author list match exactly.)

- **Method.** Uses pass@k at very large k to measure the true reasoning boundary of base vs RLVR-trained models across math/code/visual benchmarks. Finds RLVR sharpens sampling efficiency at small k but actually narrows the reachable solution set: base models match or beat RL models at large k, because RL biases the output distribution toward already-rewarded paths rather than discovering new ones.
- **Why it matters for divergence.** This is the load-bearing diagnosis for the whole theme: reward-maximizing fine-tuning trades coverage for confidence, literally shrinking the space of distinct reasoning paths a model will produce. Any harness that wants divergent thinking must counteract this distribution-narrowing, and pass@k (not pass@1) is the right yardstick for whether an agent still explores.
- **→ Harness application.** Encode pass@k thinking into the loop: for hard tasks, sample k genuinely independent attempts (high temperature / varied seeds / varied framings) and judge the SET, not the first answer — a verifier or test-suite picks the winner. Add a 'coverage budget' to a Claude Code skill that forces N distinct candidate plans before any code is written, explicitly measuring inter-candidate difference so the agent is rewarded for the union of approaches rather than collapsing to its single argmax move.

#### 2. [The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models](https://arxiv.org/abs/2505.22617)

- **Authors:** Ganqu Cui, Yuchen Zhang, Jiacheng Chen, Lifan Yuan, Zhi Wang, Yuxin Zuo, Haozhan Li, Yuchen Fan, Huayu Chen, Weize Chen, Zhiyuan Liu, Hao Peng, Lei Bai, Wanli Ouyang, Yu Cheng, Bowen Zhou, Ning Ding  
- **Year / venue:** 2025 · arXiv · arXiv:2505.22617  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2505.22617` (Title matches exactly; candidate author list was truncated with 'et al.' — full feed lists 17 authors led by Ganqu Cui, consistent with the claim.)

- **Method.** Derives that policy-entropy change during RL is governed by the covariance between a token's action probability and its logit update (advantage). Because this covariance stays positive, entropy decays monotonically; they propose Clip-Cov and KL-Cov, which clip or KL-penalize exactly the high-covariance tokens that drive the collapse, keeping exploration alive.
- **Why it matters for divergence.** Gives a mechanistic, predictive account of WHY agents collapse onto one mode: a small set of already-confident, high-advantage tokens get reinforced hardest and choke off entropy. The fix — selectively protecting high-covariance decision points from being over-sharpened — is the principle behind preserving branch diversity at exactly the tokens where reasoning forks.
- **→ Harness application.** At inference/agent time, mirror the covariance insight by identifying high-leverage 'fork' tokens (low-entropy-but-pivotal decision points: which algorithm, which file, which hypothesis) and deliberately re-sampling alternatives there instead of accepting the greedy choice. A skill could detect when the agent's candidate plans are converging (rising agreement = falling entropy) and inject a counter-pressure step that forces a divergent branch before commitment.

#### 3. [Reasoning with Exploration: An Entropy Perspective](https://arxiv.org/abs/2506.14758)

- **Authors:** Daixuan Cheng, Shaohan Huang, Xuekai Zhu, Bo Dai, Wayne Xin Zhao, Zhenliang Zhang, Furu Wei  
- **Year / venue:** 2025 · arXiv · arXiv:2506.14758  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/api/query id_list=2506.14758` (Title and full author list match exactly.)

- **Method.** Shows high-entropy tokens correlate with three exploratory behaviors — pivotal logical-branch tokens, self-verification steps, and rare/underexplored actions — then adds a clipped entropy-based term directly into the advantage function to reward (not just tolerate) those tokens, yielding longer, deeper reasoning chains and large pass@K gains.
- **Why it matters for divergence.** Reframes entropy from noise to signal: the moments where the model is uncertain are precisely where exploration, self-checking, and novel reasoning happen. Encouraging the agent to lean INTO its high-uncertainty junctures is a direct route to divergent thinking rather than confident tunnel vision.
- **→ Harness application.** Build a 'lean into uncertainty' skill: surface the model's own token-level uncertainty (or proxy it via self-reported confidence) and, at the most uncertain reasoning steps, trigger explicit branch expansion and self-verification rather than glossing over them. Reward longer reasoning at forks and insert a mandatory 'what else could this be?' verification beat whenever the agent flags low confidence.

#### 4. [Pass@k Training for Adaptively Balancing Exploration and Exploitation of Large Reasoning Models](https://arxiv.org/abs/2508.10751)

- **Authors:** Zhipeng Chen, Xiaobo Qin, Youbin Wu, Yue Ling, Qinghao Ye, Wayne Xin Zhao, Guang Shi  
- **Year / venue:** 2025 · arXiv · arXiv:2508.10751  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2508.10751` (Title and full author list match exactly.)

- **Method.** Replaces the pass@1 reward with a pass@k group reward in RLVR and derives a closed-form advantage for it, so the model is rewarded when ANY of k samples succeeds. Analysis shows exploration and exploitation are not inherently in conflict and can mutually reinforce, escaping the conservative local optimum that pass@1 drives toward.
- **Why it matters for divergence.** Directly attacks 'collapse onto one high-reward mode' at the objective level: optimizing for group success instead of single-best-answer success makes diverse, risky-but-occasionally-right paths valuable. This is the reward-shaping recipe for an agent that is allowed to gamble on novelty.
- **→ Harness application.** Adopt a pass@k objective in agent orchestration: spawn k parallel sub-agents with deliberately different strategies on the same task and score the orchestration on whether the best-of-k passes the tests, not on any single agent. A skill can allocate more parallel attempts to harder/uncertain subtasks (adaptive k), explicitly valuing a portfolio of approaches over one confident attempt.

#### 5. [CDE: Curiosity-Driven Exploration for Efficient Reinforcement Learning in Large Language Models](https://arxiv.org/abs/2509.09675)

- **Authors:** Runpeng Dai, Linfeng Song, Haolin Liu, Zhenwen Liang, Dian Yu, Haitao Mi, Zhaopeng Tu, Rui Liu, Tong Zheng, Hongtu Zhu, Dong Yu  
- **Year / venue:** 2025 · arXiv · arXiv:2509.09675  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2509.09675` (Title and full author list match exactly.)

- **Method.** Formalizes the model's own curiosity as an intrinsic exploration bonus in RLVR: actor-side curiosity = perplexity over its own generated response (penalizing overconfidence), critic-side curiosity = variance across a multi-head value estimator (count-based-style novelty). Adding these bonuses prevents premature convergence and improves AIME by ~3 points.
- **Why it matters for divergence.** Provides intrinsic-motivation signals an agent can compute about ITSELF — overconfidence and value-estimate disagreement — to know when it is failing to explore. It connects classic curiosity/count-based exploration to LLMs, giving a principled trigger for 'I'm too sure, look elsewhere.'
- **→ Harness application.** Compute cheap self-curiosity proxies in the loop: (a) if the agent's answer perplexity/confidence is suspiciously high on a non-trivial task, force generation of an alternative; (b) run an ensemble of lightweight critic prompts and when their assessments DISAGREE (high variance), treat that subproblem as under-explored and dig deeper. Wire these as a 'curiosity gate' that decides when to spend extra exploration budget.

#### 6. [Evolving Language Models without Labels: Majority Drives Selection, Novelty Promotes Variation (EVOL-RL)](https://arxiv.org/abs/2509.15194)

- **Authors:** Yujun Zhou, Zhenwen Liang, Haolin Liu, Wenhao Yu, Kishan Panaganti, Linfeng Song, Dian Yu, Xiangliang Zhang, Haitao Mi, Dong Yu  
- **Year / venue:** 2025 · arXiv · arXiv:2509.15194  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2509.15194` (Title (without the EVOL-RL parenthetical shorthand) and full author list match exactly.)

- **Method.** Label-free self-improvement that pairs a stability anchor (keep the majority-voted answer) with a novelty-aware reward that scores each sampled solution by how semantically different its reasoning is from the other concurrent samples. The selection+variation pair prevents the entropy collapse that pure self-confirmation causes (e.g., AIME25 pass@1 4.6%→16.4% on Qwen3-4B-Base).
- **Why it matters for divergence.** A direct evolutionary-computation analogue (selection for fitness, mutation for diversity) for keeping a model exploratory without external labels. The key move — explicitly rewarding reasoning that DIFFERS from siblings — is exactly the anti-collapse pressure a divergent-thinking harness needs.
- **→ Harness application.** Implement a select+vary loop: generate a batch of candidate solutions, keep the consensus answer as a stability anchor, but actively score and favor candidates whose REASONING is most semantically distinct from the rest (embed-and-diversify). In a Claude Code skill, after producing a working solution, demand a deliberately different second solution and penalize near-duplicates, maintaining a diverse 'population' of approaches across iterations.

#### 7. [The Road Less Traveled: Enhancing Exploration in LLMs via Sequential Sampling (SESA)](https://arxiv.org/abs/2510.15502)

- **Authors:** Shijia Kang, Muhan Zhang  
- **Year / venue:** 2025 · arXiv · arXiv:2510.15502  
- **Verification:** ✅ verified real — via `WebFetch arxiv.org/abs/2510.15502` (Title (without the SESA parenthetical shorthand) and author list match exactly.)

- **Method.** Instead of i.i.d. parallel sampling (which collapses to similar outputs), SESA generates diverse solution SKETCHES sequentially, each conditioned on the previously generated ones, then expands the chosen sketches into full reasoning paths. Conditioning on prior samples explicitly pushes each new attempt away from earlier ones, preventing policy collapse and yielding large agent-benchmark gains (up to 211% relative).
- **Why it matters for divergence.** Tackles the failure mode where naive multi-sampling just re-draws the same dominant mode. Sequential, diversity-conditioned generation is a decoding/agent-loop trick (no retraining needed) that forces coverage of the less-likely-but-promising branches — the 'road less traveled.'
- **→ Harness application.** Replace parallel best-of-N with sequential diverse-sketch generation in the harness: produce a short plan sketch, then prompt 'give a meaningfully different approach that does NOT overlap with the previous one(s),' feeding all prior sketches into context, until you have a spread of distinct strategies; only then expand the most promising into full implementations. This is a drop-in skill for brainstorming distinct designs before committing code.
