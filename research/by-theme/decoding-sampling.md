# Sampling & decoding strategies for diversity/novelty

*Sampling & decoding strategies for diversity/novelty*

[← back to master report](../REPORT.md)

## Key takeaways

- The single most-likely continuation (greedy/argmax) is a known failure mode: it degenerates into bland repetition. Genuine novelty lives in a middle band, off argmax but inside a coherence boundary.
- Static thresholds (fixed top-k/top-p/temperature) are suboptimal because the safe distance off argmax depends on local uncertainty. The strongest methods (eta-sampling, min-p, locally-typical) make truncation adaptive to the model's per-step entropy/confidence.
- Contrastive methods (contrastive decoding, DoLa) show novelty can be steered by subtraction: explicitly suppress the generic/obvious/premature baseline (an 'amateur' model or an early layer) to surface distinctive, higher-information content.
- Diversity can be enforced structurally, not just stochastically: Diverse Beam Search adds an explicit inter-candidate dissimilarity penalty so options span the space rather than cluster on paraphrases of the top answer.
- Mode collapse is partly an alignment artifact (typicality bias in preference data), and Verbalized Sampling shows it can be undone at the prompt level alone, no decoding-knob access required, which is critical for closed agents like Claude/GPT.
- There is a consistent quality/diversity trade-off, but the frontier paper (min-p) shows you can push temperature far higher than default if truncation is confidence-scaled, decoupling 'creative' from 'incoherent.'
- Two complementary intervention layers exist for an agent: the decoding layer (temperature, min_p, typical_p, top_p when the API exposes them) and the prompt/loop layer (verbalized distributions, diverse-candidate penalties, contrast-against-baseline) which works even with no logit access.

## Harness mechanisms

- Two-pass exploration profile: an 'ideation pass' run hot (high temperature + min_p, or verbalized sampling) that emits several materially distinct solution sketches, followed by a near-greedy 'commit pass' that locks in one and writes correct code. Different decoding settings per phase of the same task.
- Verbalized-distribution ideation skill: replace every 'propose an approach' with 'propose N distinct approaches with confidence weights, including at least one deliberate long-shot,' then force the agent to seriously evaluate a non-top option. Directly ports Verbalized Sampling into a Claude Code skill, no API knobs needed.
- Contrast-against-the-obvious loop: first elicit the cliche baseline answer (cheap model or a 'lazy/generic' persona of the same model), then instruct the main agent to produce a solution that measurably diverges from that baseline, using the baseline as an explicit negative-exemplar list. Prompt-level contrastive decoding.
- Diverse-candidate penalty: when generating option k, feed it the key design choices of options 1..k-1 with an instruction to maximize dissimilarity (different library/algorithm/architecture). Reproduces Diverse Beam Search's inter-group penalty so the agent's option set spans the space instead of paraphrasing the argmax.
- Uncertainty-aware divergence controller: at decision points, inspect the model's entropy/logprobs (where available) and widen the search (more samples, higher temp) only at high-entropy junctures (genuine design forks) while staying tight at low-entropy mechanical steps. Implements eta-sampling's adaptive-truncation idea at the agent-loop level.
- Fast-vs-deliberate self-contrast (DoLa analog): capture the snap first-draft answer, run a deeper deliberation pass, and prefer conclusions that survive deeper analysis over the premature one, filtering cheap defaults while keeping grounded novelty.
- Decoding-knob presets exposed as named modes: 'brainstorm' (temp 1.3-1.5 + min_p 0.05 / typical_p), 'balanced', 'precise' (temp 0.2, near-greedy), so the harness can switch the model's divergence level explicitly per subtask rather than relying on one global temperature.

## Papers

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
