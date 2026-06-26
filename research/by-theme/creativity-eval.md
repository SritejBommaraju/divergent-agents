# Measuring creativity, novelty, surprise & diversity in LLM output

*Measuring creativity, novelty, surprise & diversity in LLM output*

[← back to master report](../REPORT.md)

## Key takeaways

- Creativity must be measured as novelty AND quality jointly (Padmakumar's harmonic-mean frontier; NoveltyBench's quality-weighted utility_k). Optimizing originality alone is trivially gamed by producing bad or random output, so any harness reward must gate originality on a quality check.
- Diversity needs functional equivalence classes, not surface metrics. NoveltyBench shows the right unit is 'does this response add distinct value', detected by a trained pairwise classifier / LLM-judge, not distinct-n or self-BLEU which only catch lexical variation.
- Mode collapse is largely an inference-time, fixable problem. Verbalized Sampling recovers 1.6-2.1x diversity with zero training by making the model verbalize a probability distribution and surface its tail; explicitly steering toward low-probability-but-valid branches is the lever.
- Constraint accumulation forces genuine divergence. Denial Prompting (NeoGauge) — iteratively banning the strategy just used — reliably drives an agent into fresh regions of solution space and yields a measurable count of distinct valid strategies.
- Reference-free spread scores are cheap and useful. DAT-style mean pairwise semantic distance is an automatable fitness function for divergent thinking, with sampling/temperature as a direct creativity knob (with a creativity-vs-stability trade-off).
- Calibrated LLM-judges beat raw embedding distance for human-perceived originality (Ocsai: r≈0.78 vs ≈0.19), but judges are prompt-sensitive and label-biased (Rethinking Creativity Evaluation), so they must be anchored with human-rated exemplars and periodically recalibrated.
- No single creativity metric generalizes across domains and metrics often disagree — credible proof of 'more creative' requires a multi-metric ensemble plus periodic human calibration, and metric disagreement should itself be treated as a gaming/overfitting alarm.

## Harness mechanisms

- Verbalized-sampling front door: every ideation/brainstorm skill first asks the model for N candidates WITH self-assigned probabilities, then deliberately advances candidates from the low-probability-but-still-valid tail instead of the argmax; expose the probability floor as a tunable creativity dial.
- Functional-dedup loop (NoveltyBench utility_k): generate k candidates, cluster into equivalence classes via embedding-threshold or an 'are these functionally the same?' LLM-judge, drop duplicates, and keep sampling until distinct_k plateaus; rank surviving ideas by patience-discounted cumulative utility.
- Denial loop (NeoGauge): after each solution, auto-extract its core strategy, re-prompt 'solve this WITHOUT that approach', iterate until valid moves exhaust; collect all distinct valid solutions and score them against a corpus of prior/known answers to certify off-the-beaten-path novelty.
- Originality-quality frontier selector: score every candidate on originality (n-gram/embedding distance from references or the agent's own prior outputs) and quality (LLM-judge/task metric), select by their harmonic mean, and reject any candidate that buys originality by losing quality.
- DAT spread gate: embed the key concepts of a brainstormed set and compute mean pairwise cosine distance; block shipping idea sets that are too semantically clustered and use the spread score to choose which subset to expand.
- Calibrated originality judge (Ocsai-style): use a few-shot LLM-judge anchored with human-rated high/low-originality exemplars as the reward model in best-of-k/rejection sampling, with periodic human spot-checks to detect judge drift.
- Multi-metric creativity dashboard: track spread score + distinct-class count + calibrated judge originality + originality/quality harmonic mean per run; require cross-metric agreement before claiming a creativity win, and surface metric disagreement as a single-metric-gaming alarm — this is how you PROVE the intervention worked rather than overfit one number.
- Creativity regression harness: store baseline metric distributions and A/B every prompt/skill change against them so any 'make it more divergent' edit must demonstrably push diversity/novelty up without dropping quality, just as code changes pass tests.

## Papers

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
