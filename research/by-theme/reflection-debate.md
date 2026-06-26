# Self-reflection, critique & multi-agent debate

*Self-reflection, critique & multi-agent debate*

[← back to master report](../REPORT.md)

## Key takeaways

- Reflection polishes, debate diverges. Single-model iterative self-critique (Self-Refine, Reflexion) reliably improves surface quality and catches errors against an external signal, but it tends to redistribute within the model's existing idea rather than find a new one. Genuine novelty in this literature comes from enforced disagreement across independent vantage points.
- Degeneration-of-Thought is the core failure mode (Liang et al.): once an LLM is confident in its first answer, reflection rationalizes rather than revises it. The fix is structural — adversarial roles ('tit-for-tat') plus a separate judge — not more or better self-reflection prose.
- Intrinsic self-correction can HURT (Huang et al., ICLR'24): with no external/oracle signal, self-correction on reasoning tasks often stays flat or degrades because the model has no reliable internal error detector. Therefore every critique loop in a harness must be gated on real external signal (tests, execution, retrieval, a different model) — never 'reflect again with no new information'.
- Diversity is the active ingredient, not agent count (Hegazy). Heterogeneous models/personas debating beat N identical copies (91% vs 82% on GSM-8K). Identical agents converge to a shared prior; the value of debate is proportional to how genuinely different the participants' starting points are.
- Anchor critique to an explicit rubric (Constitutional AI). Open-ended 'is this good?' self-critique is unreliable; critique against a written constitution/standard is checkable and steerable. A 'novelty constitution' can make a critic actively penalize the obvious, most-likely answer.
- Diverge at the meta level too (Self-Discover): deliberately composing the reasoning structure — and including operators like 'generate alternatives' or 'invert the problem' — steers the model off its default chain at far lower compute than brute-force sampling/self-consistency.
- Practical pipeline shape: DIVERGE first (heterogeneous parallel agents / adversarial debate / structured alternative-generation) to widen the answer space, THEN converge (judge), THEN polish (Self-Refine). Conflating the polish phase with the divergence phase is how harnesses fool themselves into thinking iteration produced novelty.

## Harness mechanisms

- Devil's-advocate debate skill: spawn an Affirmative agent (defends the current plan/answer) and a Negative agent forbidden from agreeing in early rounds and rewarded for proposing a structurally DIFFERENT approach, plus a Judge agent that scores both on evidence before deciding. Implements Liang et al.'s tit-for-tat + judge to break Degeneration-of-Thought.
- Heterogeneity-maximizing ensemble: before debating, instantiate agents with deliberately distinct personas/models/temperatures/tool-budgets (skeptic, domain expert, contrarian, first-principles thinker), measure inter-agent answer diversity, and if diversity is low, perturb roles BEFORE spending debate rounds — operationalizes Hegazy's finding that diversity, not count, drives gains.
- External-signal gate on all critique loops: a harness rule that forbids 'reflect again with no new information.' Every self-correction iteration must be backed by a fresh external signal (run tests, execute code, fetch docs, query another model); track per-round whether the answer changed and whether it helped, aborting loops that degrade — directly addresses Huang et al.
- Novelty constitution: an explicit written rubric the critic judges against ('reject the first obvious solution; require >=1 non-standard approach; flag if the answer matches the most common known pattern; name the assumption that would have to be false for a different answer to win'). Turns vague self-critique into a checkable, divergence-promoting gate (Constitutional-AI pattern repurposed for novelty).
- Structured divergence pre-step (Self-Discover style): before solving, the agent selects reasoning operators from a library and must always include a divergence operator — 'propose two fundamentally different approaches and argue for each before choosing' — written into an explicit PLAN it then executes.
- Persistent reflection memory with anti-repeat check (Reflexion): a REFLECTIONS.md the agent appends 'wrong assumption + try-instead' notes to after each failure, and a diff-gate that rejects any retry whose plan is too similar to a previously-failed reflection — forcing each attempt to be materially different.
- Three-phase pipeline orchestration: DIVERGE (heterogeneous parallel/adversarial generation) -> CONVERGE (judge synthesizes) -> POLISH (Self-Refine micro-loop), with the polish phase explicitly walled off so quality refinement is never mistaken for exploration. A diversity metric on the diverge phase output decides whether to widen further before converging.

## Papers

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
