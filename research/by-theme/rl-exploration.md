# Exploration, curiosity & intrinsic motivation for reasoning agents

*Exploration, curiosity & intrinsic motivation for reasoning agents*

[← back to master report](../REPORT.md)

## Key takeaways

- Reward-maximizing fine-tuning systematically NARROWS, not widens, the reachable solution set: RLVR boosts pass@1 but base models match/beat it at large pass@k (2504.13837). The default failure mode of a trained agent is confident tunnel vision, so divergence must be engineered against the grain of the objective.
- Entropy collapse has a mechanistic cause — the positive covariance between token probability and advantage means already-confident, high-reward tokens get reinforced hardest and choke exploration (2505.22617). Collapse is predictable and can be counteracted at specific 'fork' tokens rather than globally.
- High entropy/uncertainty is signal, not noise: uncertain tokens coincide with pivotal logical branches, self-verification, and rare behaviors (2506.14758). The right policy is to LEAN INTO uncertainty at decision points, not smooth it away.
- Measuring and rewarding the SET of attempts (pass@k) instead of the single best (pass@1) dissolves the false exploration/exploitation conflict — they can mutually reinforce (2508.10751). Optimize portfolios of approaches, not one confident answer.
- An agent can self-detect under-exploration with cheap intrinsic signals it computes about itself: own-output overconfidence/perplexity, and disagreement (variance) across multiple critic/value estimates (2509.09675). These give a principled 'when to explore more' trigger.
- Diversity must be made an explicit reward, not hoped for: scoring candidates by how semantically DIFFERENT their reasoning is from siblings (EVOL-RL, 2509.15194) is the core anti-collapse pressure, even label-free, and is a direct evolutionary selection+variation analogue.
- Naive parallel multi-sampling re-draws the dominant mode; SEQUENTIAL generation conditioned on prior samples ('be different from what you already produced') is a retrain-free decoding/agent-loop trick that actually achieves coverage (2510.15502).

## Harness mechanisms

- Coverage-budget skill (pass@k loop): for any non-trivial task, require N genuinely distinct candidate plans/solutions before committing; score the harness on best-of-N against tests/verifier, not on the first answer. Adaptively raise N for subtasks flagged as hard or uncertain.
- Diversity-conditioned sequential brainstorming (SESA-style): generate plan sketches one at a time, each prompt explicitly fed all prior sketches with an instruction to take a meaningfully non-overlapping approach; embed-and-deduplicate to reject near-clones, then expand only the most distinct/promising sketches into code.
- Explicit novelty reward (EVOL-RL-style selection+variation): keep a consensus answer as a stability anchor but actively favor the candidate whose reasoning is most semantically distant from the rest; maintain a persistent 'population' of approaches across iterations and penalize regression to a single mode.
- Curiosity gate (CDE-style intrinsic trigger): compute self-confidence/perplexity on the agent's own answer and run an ensemble of lightweight critic prompts; when confidence is suspiciously high OR critics disagree (high variance), spend extra exploration budget and force an alternative line of attack.
- Fork-token re-sampling (entropy-mechanism-style): detect pivotal decision points (which algorithm/file/hypothesis) and deliberately re-sample alternatives there instead of accepting the greedy choice — protect high-leverage forks from premature commitment, mirroring Clip-Cov/KL-Cov's selective protection of high-covariance tokens.
- Lean-into-uncertainty beat: at the agent's most uncertain reasoning steps, mandatorily insert a 'what else could this be?' branch-and-self-verify step and reward deeper reasoning there, converting uncertainty into exploration rather than glossing it over.
- Collapse monitor: track inter-candidate agreement / output entropy across a session as a live proxy for the policy narrowing; when agreement rises past a threshold (exploration vanishing), automatically inject a counter-pressure divergent branch before any final commitment.
- Pass@k-not-pass@1 evaluation harness: judge divergence quality by the union/coverage of distinct correct approaches across attempts (large-k mindset) so the agent is explicitly credited for reaching solutions outside its single argmax move.

## Papers

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
