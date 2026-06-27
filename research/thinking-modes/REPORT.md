# Thinking modes — the grounded cognitive library

*Verified evidence base for the Cognitive Engine (`engine/`). Each mode operator below is grounded in a real, re-checked paper. 36/36 papers confirmed real.*


## Deductive, inductive & abductive reasoning in LLMs

**Routing signals — when this family of thinking is needed**

- DEDUCTIVE (forward): inputs include an explicit closed set of premises/rules and the question asks what necessarily follows, or to compute an answer that must be provable — route to Forward Deductive Chaining + Deductive Verification.
- DEDUCTIVE (backward): a single specific claim must be proved/refuted against a large rule/knowledge base, or required proof depth is high and forward search would explode — route to Backward Goal-Decomposition.
- INDUCTIVE: only examples/observations are given and a general rule, pattern, function, or program must be inferred and then reused — route to Inductive Hypothesis Search; if the rules should persist for reuse, add the HtT induction->deduction pipeline.
- ABDUCTIVE: an outcome/symptom/anomaly is given and the task is to infer the most likely cause or explanation among several non-forced possibilities (diagnosis, root cause, 'why') — route to Abductive Best-Explanation Selection.
- Validity-critical: whenever an answer's correctness is high-stakes or a long chain risks error accumulation, wrap the chosen operator in the Deductive Verification Gate before committing.
- Direction cue: 'given rules -> derive facts' = deduction; 'given examples -> derive rule' = induction; 'given facts -> derive cause' = abduction. The arrow direction between data and rule is the primary router.
- Certainty cue: necessity/entailment language ('must', 'follows', 'prove') => deductive; generalization language ('pattern', 'usually', 'rule from these') => inductive; best-guess/explanatory language ('most likely', 'because', 'explains') => abductive (defeasible, return with confidence).

**Mode operators**

- **Forward Deductive Chaining (Select-then-Infer)** *(deductive)* — trigger: You have a set of given premises/rules/facts and must derive what necessarily follows, or check whether a conclusion is entailed. Signals: 'given that... what follows', closed-world rule sets, math/logic word problems, policy/eligibility rules, multi-hop entailment where the answer must be PROVABLE from inputs, not guessed.
  - protocol: 1. State the goal and list all available premises explicitly. 2. SELECTION: pick the minimal subset of premises relevant to the current frontier. 3. INFERENCE: derive exactly ONE new fact entailed by only that subset; write the derivation citing the premises used. 4. Add the new fact to the pool; repeat 2-3. 5. Stop when the goal is derived (proven), its negation is derived (refuted), or no new facts can be produced (cannot determine). 6. Emit the ordered step list as the proof trace. Never introduce a fact not entailed by selected premises.
  - grounding: Selection-Inference (Creswell et al., arXiv:2205.09712)
- **Backward Goal-Decomposition Proof** *(decompositional)* — trigger: The task is to prove/refute ONE specific target claim against a large rule base, and forward derivation would explode (many irrelevant facts, deep chains, negation/polarity matters). Signals: yes/no entailment over big knowledge bases, 'is X true given these rules', long required proof depth, need to avoid enumerating everything derivable.
  - protocol: 1. Set the claim as the top goal. 2. Fact-check: is the goal directly stated? If yes, resolve. 3. Rule-select: find rules whose conclusion unifies with the goal. 4. Goal-decompose: for a chosen rule, make its premises new subgoals; recurse on each. 5. Sign/polarity check: track negation so you prove the goal with the correct truth sign. 6. A goal succeeds if a supporting rule's subgoals all succeed (or it's a known fact); fails if exhausted. 7. Return PROVED / DISPROVED / UNKNOWN with the assembled subgoal tree. Prefer this over forward chaining when depth is high or the rule base is large.
  - grounding: LAMBADA: Backward Chaining for Automated Reasoning (Kazemi et al., arXiv:2212.13894)
- **Inductive Hypothesis Search (Generalize-then-Test)** *(inductive)* — trigger: You must infer a general rule/pattern/program from a handful of examples or observations, then apply it to new cases. Signals: few-shot 'find the rule', sequence/transformation puzzles (ARC-style), 'what's the pattern', schema/function induction, generalizing from data where a single direct answer is unreliable.
  - protocol: 1. Collect all observed (input, output) examples. 2. GENERATE several distinct candidate hypotheses in natural language, at varied abstraction levels (don't commit to one). 3. Make each testable: express it concretely (e.g. as a program or precise predicate). 4. FALSIFY: run/check every candidate against ALL examples; discard any that misfit even one. 5. Among survivors prefer the simplest (Occam) that covers all data. 6. If none survive, generate new hypotheses informed by the failures and repeat. 7. Apply the surviving rule to the query; report the rule itself as the justification.
  - grounding: Hypothesis Search (Wang et al., arXiv:2309.05660); Hypotheses-to-Theories / HtT (Zhu et al., arXiv:2310.07064)
- **Abductive Best-Explanation Selection** *(abductive)* — trigger: You observe an outcome/symptom/surprising fact and must infer the most plausible CAUSE or explanation — multiple explanations are possible and none is logically forced. Signals: diagnosis, root-cause analysis, 'why did this happen', incident triage, interpreting incomplete evidence, detective-style inference where you choose among competing stories.
  - protocol: 1. Fix the observations to be explained. 2. ENUMERATE several competing candidate explanations (force breadth; don't anchor on the first). 3. For each, derive what it would predict and check it against the observations. 4. SCORE each on explicit IBE criteria: logical consistency (no contradiction with evidence), explanatory coverage, parsimony (fewest assumptions), coherence with background knowledge, and flag linguistic/epistemic uncertainty. 5. Select the highest-scoring explanation as 'best', but keep the runner-up and state the discriminating test that would separate them. 6. Report it as a defeasible hypothesis with confidence, not a proof.
  - grounding: Inference to the Best Explanation in LLMs / IBE-Eval (Dalal et al., arXiv:2402.10767)
- **Deductive Verification Gate** *(deductive)* — trigger: Any time a reasoning chain has been produced (by CoT, induction, or abduction) and its correctness matters — before committing to an answer. Signals: high-stakes answer, long CoT prone to error accumulation, claims that must each follow from stated premises, audit/'check the work' requests.
  - protocol: 1. Reformat the chain so each step explicitly cites the premises/prior steps it depends on (Natural Program style). 2. For each step IN ISOLATION, present only its cited premises and ask: does the conclusion follow validly? 3. Mark any step that introduces unsupported information or a non-sequitur as invalid. 4. If any step fails, reject the chain and regenerate from that point; if all pass, accept. 5. Use this as a wrapper around the other operators — it certifies validity, it does not generate new content.
  - grounding: Deductive Verification of Chain-of-Thought Reasoning (Ling et al., arXiv:2306.03872)

**Papers**

- ✅ [Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning](https://arxiv.org/abs/2205.09712) — *Antonia Creswell, Murray Shanahan, Irina Higgins* (2022, arXiv:2205.09712)  
  **Finding.** Splits deduction into two alternating LLM calls — SELECTION (pick the subset of premises/facts relevant to the current goal) and INFERENCE (derive one new fact from only that selected subset). Iterating produces a causal, auditable natural-language proof trace. A 7B model in this framework (5-shot, no fine-tuning) beat a vanilla baseline by >100% on a suite of 10 logical-reasoning tasks, because each step is grounded only in explicitly selected premises rather than free-form generation.  
  **Grounds.** Grounds the FORWARD DEDUCTIVE CHAINING operator: derive entailed conclusions one validated step at a time, each step consuming an explicitly selected premise set so no claim outruns its support.  
  *Verified via WebFetch arxiv.org/abs/2205.09712.*
- ✅ [LAMBADA: Backward Chaining for Automated Reasoning in Natural Language](https://arxiv.org/abs/2212.13894) — *Mehran Kazemi, Najoung Kim, Deepti Bhatia, Xin Xu, Deepak Ramachandran* (2022, arXiv:2212.13894)  
  **Finding.** Forward proof search explodes combinatorially and fails on long chains. LAMBADA instead chains BACKWARD from the goal, decomposing reasoning into four few-shot LLM sub-modules — Fact Check, Rule Selection, Goal Decomposition, and Sign Agreement (polarity/negation handling). Working goal->subgoals->facts yields large accuracy gains over forward methods (CoT, Selection-Inference) especially as required proof depth grows, while using far fewer inference calls.  
  **Grounds.** Grounds the BACKWARD GOAL-DECOMPOSITION PROOF operator: when you must prove/refute a specific target, recurse from the goal to the rules that could establish it and the subgoals they need, rather than enumerating everything derivable.  
  *Verified via WebFetch arxiv.org/abs/2212.13894.*
- ✅ [Deductive Verification of Chain-of-Thought Reasoning](https://arxiv.org/abs/2306.03872) — *Zhan Ling, Yunhao Fang, Xuanlin Li, Zhiao Huang, Mingu Lee, Roland Memisevic, Hao Su* (2023, arXiv:2306.03872)  
  **Finding.** Introduces 'Natural Program', a structured CoT format where every step lists exactly which prior premises it uses. Verification is decomposed: each step is checked in isolation against only its cited premises, so a single invalid step can be caught and rejected without re-reading the whole chain. This isolation-based deductive verification reduces hallucinated/accumulated errors and improves final accuracy on GSM8K and MATH.  
  **Grounds.** Grounds the DEDUCTIVE VERIFICATION operator — a check phase that re-pins each generated step to its declared premises and rejects non-sequiturs; the validity gate that makes any deductive chain trustworthy.  
  *Verified via WebFetch arxiv API id_list=2306.03872.*
- ✅ [Hypothesis Search: Inductive Reasoning with Language Models](https://arxiv.org/abs/2309.05660) — *Ruocheng Wang, Eric Zelikman, Gabriel Poesia, Yewen Pu, Nick Haber, Noah D. Goodman* (2023, arXiv:2309.05660)  
  **Finding.** For induction from few examples, generating one answer directly is weak. Instead prompt the LLM to propose MULTIPLE explicit candidate rules (hypotheses) in natural language at varying abstraction levels, then make each concrete by compiling it to a Python program and EXECUTING it against the given examples to filter. On an ARC subset this pipeline hit 30% vs 17% direct prompting (33% with light human selection), showing that hypothesis generation + empirical falsification beats one-shot guessing.  
  **Grounds.** Grounds the INDUCTIVE HYPOTHESIS SEARCH operator: from observations, generate many candidate general rules, then verify each against all data and keep only survivors — generalize-then-test rather than pattern-match.  
  *Verified via WebFetch arxiv.org/abs/2309.05660.*
- ✅ [Large Language Models can Learn Rules](https://arxiv.org/abs/2310.07064) — *Zhaocheng Zhu, Yuan Xue, Xinyun Chen, Denny Zhou, Jian Tang, Dale Schuurmans, Hanjun Dai* (2023, arXiv:2310.07064)  
  **Finding.** Hypotheses-to-Theories (HtT) makes the induction/deduction split explicit and persistent. INDUCTION stage: over training examples, the LLM proposes rules and keeps only those that appear often and lead to correct answers, forming a reusable rule LIBRARY. DEDUCTION stage: at test time the LLM reasons by retrieving and applying that fixed library. Gains of 10-30% absolute on relational, numerical, and concept-learning tasks; learned rules transfer across models and problem phrasings.  
  **Grounds.** Grounds the two-phase INDUCTION->DEDUCTION pipeline: induce a verified rule library once, then switch into deductive application mode against it — showing the modes are composable, not just alternatives.  
  *Verified via WebFetch arxiv.org/abs/2310.07064.*
- ✅ [Inference to the Best Explanation in Large Language Models](https://arxiv.org/abs/2402.10767) — *Dhairya Dalal, Marco Valentino, André Freitas, Paul Buitelaar* (2024, arXiv:2402.10767)  
  **Finding.** Operationalizes abduction (Inference to the Best Explanation) as explicit scoring. IBE-Eval ranks competing candidate explanations using interpretable features — logical consistency, parsimony (simplicity), coherence, and linguistic uncertainty — rather than picking the most fluent one. It identifies the best explanation with up to 77% accuracy (~27% above random) and beats GPT-3.5-as-a-judge by ~17%, while being cheaper and interpretable.  
  **Grounds.** Grounds the ABDUCTIVE BEST-EXPLANATION operator: given observations, enumerate competing hypotheses and select the one that best scores on consistency + parsimony + coherence — the explicit criteria that define 'best' explanation.  
  *Verified via WebFetch arxiv.org/abs/2402.10767.*


## Reasoning-structure selection, metacognition & adaptive routing

**Routing signals — when this family of thinking is needed**

- The engine has multiple reasoning modes registered and the incoming task does not name a method — a selection step is required before any solving begins.
- Heterogeneous task stream (easy and hard interleaved) under a stated compute, token, or latency budget — calls for Diagnose-and-Route + Think-Long-vs-Short.
- Task is novel/compound and no single template fits, or it explicitly chains kinds of thinking ('analyze then design then critique') — triggers Compose-Reasoning-Structure.
- Problem features signal a specific non-divergent family (constraints+'prove/derive' -> deductive; 'why did X happen' -> causal; 'how likely / under uncertainty' -> probabilistic; 'break this down' -> decompositional) — route there instead of defaulting to brainstorming.
- High-stakes or single-shot answer where a confident wrong reply is costly — triggers Metacognitive-Monitor-and-Calibrate before commit.
- The agent's internal confidence is high but the task is multi-step or out-of-distribution — treat as overconfidence risk and down-weight self-estimate before routing.
- Observed overthinking (long reasoning degrading easy items) or repeated overruns — switch to short-path default with escalation gating.
- A first-pass attempt fails a self-consistency / verification check — escalate to a deeper tier or the pre-recorded fallback mode rather than retrying the same mode.

**Mode operators**

- **Diagnose-and-Route** *(metacognitive)* — trigger: A task arrives with no obvious method, OR the engine has several reasoning modes available and applying the wrong/most-expensive one by default is wasteful or error-prone. Signals: heterogeneous task stream, explicit compute/latency budget, 'pick the right approach' framing.
  - protocol: 1) Extract problem features: domain, required output type, presence of constraints/data/multiple steps, ambiguity. 2) Map features to a candidate reasoning family (deductive, causal, probabilistic, decompositional, divergent, analogical...). 3) Estimate difficulty tier (trivial / single-step / multi-step). 4) Select the cheapest family x depth predicted to solve it; record the alternative as fallback. 5) Dispatch to that mode; if it fails a self-check, escalate to the fallback. Treat this as classification, not solving — do not start answering until a mode is chosen.
  - grounding: Route to Reason (2505.19435); Adaptive-RAG (2403.14403)
- **Compose-Reasoning-Structure** *(metacognitive)* — trigger: The problem is novel or compound — no single canned template (plain CoT) fits, and it plausibly needs several kinds of thinking stitched together (e.g. decompose THEN critique THEN compute).
  - protocol: 1) SELECT: from a library of atomic reasoning modules (decompose, list assumptions, critical-think, reason step-by-step, consider alternatives, work backwards, estimate, check units) pick the few relevant to THIS task. 2) ADAPT: rephrase each chosen module in the task's own terms. 3) IMPLEMENT: arrange them into an explicit ordered plan/structure (key-value steps). 4) EXECUTE the structure to produce the answer. 5) Keep the structure as a reusable artifact for similar tasks.
  - grounding: Self-Discover (2402.03620)
- **Metacognitive-Monitor-and-Calibrate** *(metacognitive)* — trigger: Output correctness matters and a first-pass answer could be confidently wrong; or the agent must decide whether to commit, abstain, or gather more. Signals: high-stakes decision, single-shot answer demanded, agent feels 'sure' (overconfidence risk).
  - protocol: 1) Produce a preliminary judgment/answer. 2) Critically evaluate it: surface the assumptions, look for a counter-interpretation, check against the input. 3) Revise or confirm with explicit reasoning. 4) Emit a CALIBRATED confidence — and deliberately discount it, since raw self-estimates skew overconfident, especially on multi-step tasks. 5) Route on the calibrated value: high -> commit; medium -> escalate effort or seek evidence; low -> abstain/ask.
  - grounding: Metacognitive Prompting (2308.05342); Do LLMs Know What They Are Capable Of? (2512.24661)
- **Think-Long-vs-Short (Effort Budgeting)** *(metacognitive)* — trigger: Tasks vary widely in difficulty and spending full deliberation on every one is too slow/expensive, OR there is a known overthinking failure where extended reasoning derails easy items.
  - protocol: 1) Quick-glance the instance for difficulty cues (small arithmetic vs multi-hop, single fact vs synthesis). 2) If cues say easy/known: answer directly (short path), skip the chain. 3) If cues say hard/uncertain/multi-step: allocate a long deliberation budget (full structure, search, verification). 4) Mid-stream, if a 'short' attempt hits an inconsistency or low confidence, escalate to long. 5) Cap depth at the tier chosen to prevent runaway overthinking.
  - grounding: AutoL2S (2505.22662); Route to Reason (2505.19435)

**Papers**

- ✅ [Self-Discover: Large Language Models Self-Compose Reasoning Structures](https://arxiv.org/abs/2402.03620) — *Pei Zhou, Jay Pujara, Xiang Ren, Xinyun Chen, Heng-Tze Cheng, Quoc V. Le, Ed H. Chi, Denny Zhou, Swaroop Mishra, Huaixiu Steven Zheng* (2024, arXiv:2402.03620)  
  **Finding.** An LLM, given a pool of ~39 atomic reasoning modules (e.g. 'critical thinking', 'break into subproblems', 'step-by-step'), first SELECTS the modules relevant to a task, ADAPTS their wording to the task, then IMPLEMENTS them into an explicit JSON reasoning structure it follows during decoding. Beats CoT by up to 32% on BigBench-Hard, MATH and agent reasoning, and beats CoT-Self-Consistency by >20% at 10-40x less inference compute.  
  **Grounds.** Grounds the COMPOSE operator: meta-reasoning that picks-and-assembles atomic reasoning primitives into a task-specific structure rather than applying one fixed chain.  
  *Verified via arxiv API id_list=2402.03620.*
- ✅ [Metacognitive Prompting Improves Understanding in Large Language Models](https://arxiv.org/abs/2308.05342) — *Yuqing Wang, Yun Zhao* (2023, arXiv:2308.05342)  
  **Finding.** Introduces a 5-stage introspective loop modeled on human metacognition: (1) comprehend the input, (2) form a preliminary judgment, (3) critically evaluate that judgment, (4) commit to a final decision with reasoning, (5) assess confidence. Across 10 NLU datasets and four LLMs (GPT-4, GPT-3.5, PaLM2, Llama2) it consistently outperforms standard and chain-of-thought prompting on nuanced understanding tasks.  
  **Grounds.** Grounds the METACOGNITIVE-MONITOR operator: an agent 'thinks about its own thinking' — generating a tentative answer, then auditing and recalibrating it before committing.  
  *Verified via arxiv API id_list=2308.05342.*
- ✅ [Route to Reason: Adaptive Routing for LLM and Reasoning Strategy Selection](https://arxiv.org/abs/2505.19435) — *Zhihong Pan, Kai Zhang, Yuze Zhao, Yupeng Han* (2025, arXiv:2505.19435)  
  **Finding.** A unified, plug-and-play router learns compressed task representations and at inference time jointly selects BOTH the model and the reasoning strategy (from seven models x four strategies) to fit task complexity under a compute budget. Achieves higher accuracy than the best single model while cutting token usage by over 60%, and avoids 'overthinking' where heavy test-time scaling gets stuck in flawed reasoning paths.  
  **Grounds.** Grounds the DIAGNOSE-AND-ROUTE operator: a meta-classifier that maps a problem's features to the cheapest reasoning mode/strategy expected to solve it.  
  *Verified via arxiv API id_list=2505.19435.*
- ✅ [Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity](https://arxiv.org/abs/2403.14403) — *Soyeong Jeong, Jinheon Baek, Sukmin Cho, Sung Ju Hwang, Jong C. Park* (2024, arXiv:2403.14403)  
  **Finding.** Trains a small classifier (a smaller LM) to predict query complexity into three tiers — no-retrieval, single-step retrieval, iterative multi-step retrieval — using labels mined automatically from which strategy actually succeeded. The router seamlessly escalates effort only as the question demands, beating both always-simple and always-complex pipelines on accuracy/efficiency.  
  **Grounds.** Grounds the EFFORT-TIERING operator: a learned complexity gate that escalates from zero-shot to single-step to iterative deliberation, the routing analog applied to depth-of-search.  
  *Verified via arxiv API id_list=2403.14403.*
- ✅ [AutoL2S: Auto Long-Short Reasoning for Efficient Large Language Models](https://arxiv.org/abs/2505.22662) — *Feng Luo, Yu-Neng Chuang, Guanchu Wang, Hoang Anh Duy Le, Shaochen Zhong, Hongyi Liu, Jiayi Yuan, Yang Sui, Vladimir Braverman, Vipin Chaudhary, Xia Hu* (2025, arXiv:2505.22662)  
  **Finding.** Trains a lightweight switch so the model itself decides, per instance, whether a short answer suffices or long chain-of-thought is needed ('think thoroughly but only when necessary'), using mixed long/short CoT training data with a special token signal. Cuts reasoning length by up to 71% with minimal accuracy loss by reserving deep deliberation for genuinely hard inputs.  
  **Grounds.** Grounds the THINK-LONG-VS-SHORT operator: an instance-level budget decision on how much deliberation to spend before answering.  
  *Verified via arxiv abs page (API returned 429; verified via https://arxiv.org/abs/2505.22662).*
- ✅ [Do Large Language Models Know What They Are Capable Of?](https://arxiv.org/abs/2512.24661) — *Casey O. Barkan, Sid Black, Oliver Sourbut* (2025, arXiv:2512.24661)  
  **Finding.** Tests whether LLMs can predict their own success and finds all tested models are systematically overconfident; capability calibration degrades further on multi-step tasks. Decisions are 'approximately rational given their estimated probabilities of success, yet overly-optimistic estimates result in poor decision making' — i.e. the meta-layer's self-estimate, not its reasoning, is the bottleneck.  
  **Grounds.** Grounds the CALIBRATE / KNOW-WHAT-YOU-KNOW operator and is the cautionary basis for routing: a router that trusts the model's raw confidence will under-escalate, so confidence must be corrected before it drives mode selection.  
  *Verified via arxiv abs page (API returned 429; verified via https://arxiv.org/abs/2512.24661).*


## Decomposition, planning & least-to-most reasoning

**Routing signals — when this family of thinking is needed**

- Request explicitly chains steps with data dependencies — 'compute/find X, then use X to do Y' — so a later part cannot start until an earlier part is solved.
- The task is visibly harder or longer than worked examples available, or demands compositional generalization (assemble known operations into a longer/novel procedure).
- Multi-part deliverable where the dominant failure mode is omitting a step or drifting mid-solution (favors writing a plan before solving).
- Open-ended/agentic task of unknown depth, or one stubborn sub-step keeps failing while others are trivial — depth of decomposition should adapt (recurse only where execution fails).
- Complexity comes from input length/scale (long document, large list) that should be split into same-shape sub-instances and recombined.
- A step admits several viable continuations with real dead-ends, so backtracking/search beats a single linear chain (puzzles, planning, optimization, constraint satisfaction).
- Partial results must be aggregated, merged, deduplicated, or synthesized back together (map-then-reduce / sort / set-operation shapes).
- User phrasing like 'break this down', 'step by step plan', 'first... then...', 'how would you approach', 'outline the steps before doing it'.
- A previous single-shot or pure-divergent attempt produced a plausible-looking but wrong answer with a skipped or out-of-order step — signal to switch from generation to ordered decomposition.

**Mode operators**

- **Least-to-Most Subgoal Ordering** *(decompositional)* — trigger: The problem is harder than any single worked example you can recall; it has a natural 'you must solve A before you can even state B' dependency; or compositional generalization is required (combine known pieces into a longer/novel whole). Signals: 'multi-step', 'compute X then use it', word problems, compositional instructions.
  - protocol: 1. REDUCE: list the subproblems needed for the final answer, ordered from the one needing no prior results to the one needing the most. 2. Verify the ordering is a valid dependency chain (each item only depends on earlier items). 3. SOLVE sequentially: solve subproblem i, then APPEND its concrete answer into the working context before attempting i+1. 4. The final subproblem's solution IS the answer. Never attempt a later subgoal before its prerequisites are solved and their answers are in context.
  - grounding: Least-to-Most Prompting Enables Complex Reasoning in Large Language Models (arXiv:2205.10625)
- **Plan-then-Execute** *(decompositional)* — trigger: A request where skipping a step is the main failure risk, or where the route to the answer is non-obvious and worth committing to before spending effort. Signals: long multi-part deliverables, 'make sure you cover everything', tasks where mid-solution drift / missing-step errors are likely.
  - protocol: 1. Before any solving, write an explicit PLAN: enumerate the subtasks and their order as a standalone artifact. 2. Review the plan for completeness (are all parts of the goal covered?) and feasibility — repair the plan, not the solution. 3. EXECUTE each subtask in order, keeping intermediate variables/results explicit. 4. After execution, check each delivered piece against its plan item before finalizing. The separation is the point: planning catches omissions that linear solving hides.
  - grounding: Plan-and-Solve Prompting (arXiv:2305.04091)
- **Adaptive Recursive Decomposition (decompose only as-needed)** *(decompositional)* — trigger: Open-ended or agentic tasks of unknown depth where you can't tell upfront which parts are hard; complexity may come from input LENGTH; some sub-tasks are trivial while others are deep. Signals: 'it depends', tool-use/agent loops, a flat plan keeps failing on one stubborn step, very long inputs.
  - protocol: 1. ATTEMPT the (sub)task directly with the available solver. 2. If it succeeds, stop — do NOT decompose further. 3. If it fails or is judged too hard, invoke a planner to split it into a small ordered sub-plan, then RECURSE this same procedure on each child, dispatching each child to the most appropriate solver (a specialized prompt, a tool, a symbolic function, or another decomposition). 4. For length-driven complexity, decompose into the same task over smaller input chunks and combine. Decomposition depth thus adapts to actual difficulty and solver capability.
  - grounding: ADaPT: As-Needed Decomposition and Planning (arXiv:2311.05772); Decomposed Prompting (arXiv:2210.02406)
- **Deliberate Search-and-Merge over Thoughts** *(convergent)* — trigger: A decomposed step has MULTIPLE plausible continuations and dead-ends are real (early choices can doom the solve), OR partial results must be recombined/aggregated into the answer. Signals: search/puzzle/optimization tasks, 'find an arrangement that...', need for backtracking, map-then-reduce shapes (sort, merge, dedupe, synthesize many parts).
  - protocol: 1. Decompose into steps; at each step GENERATE several candidate next-thoughts instead of one. 2. EVALUATE each candidate state (score, or sure/maybe/impossible) for promise toward the goal. 3. SEARCH: expand promising states (BFS/DFS), prune dead-ends, and BACKTRACK when a branch is judged hopeless. 4. When sub-results are independent, run them in parallel then MERGE/aggregate and distill the combined result (graph-style), adding feedback/refinement loops as needed. 5. Return the best complete path or merged artifact.
  - grounding: Tree of Thoughts (arXiv:2305.10601); Graph of Thoughts (arXiv:2308.09687)

**Papers**

- ✅ [Least-to-Most Prompting Enables Complex Reasoning in Large Language Models](https://arxiv.org/abs/2205.10625) — *Denny Zhou, Nathanael Schärli, Le Hou, Jason Wei, Nathan Scales, Xuezhi Wang, Dale Schuurmans, Claire Cui, Olivier Bousquet, Quoc Le, Ed Chi* (2023, arXiv:2205.10625)  
  **Finding.** Introduces a two-stage strategy: first REDUCE a complex problem into a list of simpler subproblems ordered easiest-to-hardest, then SOLVE them sequentially, feeding each solved subproblem's answer into the prompt for the next. This explicitly attacks easy-to-hard generalization where chain-of-thought fails on problems harder than the exemplars. With code-davinci-002 it solves the SCAN compositional-generalization benchmark at 99.7% from only 14 examples (vs ~16% for CoT).  
  **Grounds.** Grounds the core Least-to-Most Subgoal Ordering operator — ordered subgoal decomposition with forward answer-passing as a distinct thinking mode separate from divergent generation.  
  *Verified via arxiv id_list query for 2205.10625.*
- ✅ [Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models](https://arxiv.org/abs/2305.04091) — *Lei Wang, Wanyu Xu, Yihuai Lan, Zhiqiang Hu, Yunshi Lan, Roy Ka-Wei Lee, Ee-Peng Lim* (2023, arXiv:2305.04091)  
  **Finding.** Separates planning from execution in zero-shot: the model is first instructed to 'devise a plan to divide the whole task into smaller subtasks', then to 'carry out the subtasks step by step according to the plan'. This targets the missing-step errors of plain Zero-shot-CoT; PS+ adds explicit variable-extraction and calculation instructions, matching or beating few-shot CoT on arithmetic/commonsense/symbolic benchmarks with no exemplars.  
  **Grounds.** Grounds the Plan-then-Execute operator — produce an explicit ordered plan as an artifact BEFORE solving, so missing steps are caught at plan time rather than mid-solution.  
  *Verified via arxiv id_list query for 2305.04091.*
- ✅ [Decomposed Prompting: A Modular Approach for Solving Complex Tasks](https://arxiv.org/abs/2210.02406) — *Tushar Khot, Harsh Trivedi, Matthew Finlayson, Yao Fu, Kyle Richardson, Peter Clark, Ashish Sabharwal* (2023, arXiv:2210.02406)  
  **Finding.** Decomposes a complex task via a 'decomposer' prompt into sub-tasks, each handled by a dedicated handler in a shared library; a handler can itself be another decomposer (hierarchical), a different optimized prompt, a fine-tuned model, or a symbolic function. Length-driven complexity is handled by RECURSIVE decomposition into the same task on smaller inputs. Outperforms prior few-shot prompting on symbolic and multi-hop QA tasks.  
  **Grounds.** Grounds the Recursive/Modular Decomposition operator — sub-tasks are dispatched to specialized solvers and recursively re-decomposed, treating decomposition as a software-like modular architecture.  
  *Verified via arxiv id_list query for 2210.02406.*
- ✅ [ADaPT: As-Needed Decomposition and Planning with Language Models](https://arxiv.org/abs/2311.05772) — *Archiki Prasad, Alexander Koller, Mareike Hartmann, Peter Clark, Ashish Sabharwal, Mohit Bansal, Tushar Khot* (2024, arXiv:2311.05772)  
  **Finding.** Decomposes sub-tasks recursively but only AS-NEEDED — when an executor LLM fails to complete a sub-task, a planner module breaks it into a logical sub-plan and recurses; sub-tasks that execute fine are never decomposed. This adapts decomposition depth to both task complexity and the executor's capability, beating plan-and-execute and ReAct-style iterative baselines by up to 28.3% (ALFWorld), 27% (WebShop), 33% (TextCraft).  
  **Grounds.** Grounds the As-Needed (Adaptive-Depth) Decomposition operator — don't pre-plan everything; attempt directly, and recurse into decomposition only at the points where execution actually fails.  
  *Verified via arxiv id_list query for 2311.05772.*
- ✅ [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601) — *Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L. Griffiths, Yuan Cao, Karthik Narasimhan* (2023, arXiv:2305.10601)  
  **Finding.** Frames problem-solving as search over a tree of intermediate 'thoughts': at each decomposed step the model generates multiple candidate next-thoughts, self-evaluates each (sure/maybe/impossible or value scores), and uses BFS/DFS with lookahead and backtracking to choose globally. Game of 24 jumps from 4% (CoT) to 74% success; also strong on creative writing and mini-crosswords.  
  **Grounds.** Grounds the Deliberate Search-over-Decomposition operator — when a subgoal has multiple viable continuations and dead-ends exist, decomposition becomes an explicit search with state evaluation and backtracking rather than a single linear chain.  
  *Verified via arxiv id_list query for 2305.10601.*
- ✅ [Graph of Thoughts: Solving Elaborate Problems with Large Language Models](https://arxiv.org/abs/2308.09687) — *Maciej Besta, Nils Blach, Ales Kubicek, Robert Gerstenberger, Michal Podstawski, Lukas Gianinazzi, Joanna Gajda, Tomasz Lehmann, Hubert Niewiadomski, Piotr Nyczyk, Torsten Hoefler* (2024, arXiv:2308.09687)  
  **Finding.** Generalizes Tree of Thoughts by modeling reasoning as an arbitrary GRAPH where thoughts are vertices and edges are dependencies, enabling aggregation/merging of multiple thoughts, distillation of whole sub-networks, and feedback loops — not just tree branching. Improves sort quality by 62% over ToT while cutting cost >31%, fitting tasks (sorting, set ops, keyword counting) that decompose then RECOMBINE partial results.  
  **Grounds.** Extends the search operator to the merge/aggregate case — grounds decomposition where sub-results must be combined back together (map-then-reduce planning), not only branched and pruned.  
  *Verified via arxiv id_list query for 2308.09687.*
- ✅ [Successive Prompting for Decomposing Complex Questions](https://arxiv.org/abs/2212.04092) — *Dheeru Dua, Shivanshu Gupta, Sameer Singh, Matt Gardner* (2022, arXiv:2212.04092)  
  **Finding.** Interleaves decomposition and answering: rather than emitting the full chain at once, the model alternates 'ask next simple sub-question' then 'answer it', repeating until the final answer — decoupling the supervision for HOW to decompose from the supervision for answering each step, and allowing fresh in-context examples and bespoke solvers per step. Gains ~5% absolute F1 on few-shot DROP.  
  **Grounds.** Grounds the Interleaved Decompose-then-Solve loop — generate only the next subproblem given the current state, answer it, repeat; a dynamic (vs upfront-static) variant of least-to-most for open-ended multi-hop problems.  
  *Verified via arxiv id_list query for 2212.04092.*


## Causal, counterfactual & probabilistic/Bayesian reasoning

**Routing signals — when this family of thinking is needed**

- Query contains intervention verbs: 'do', 'force', 'set', 'intervene', 'if we deploy/treat/ban X', 'effect of doing X' — needs Rung-2 reasoning, not association.
- Counterfactual/subjunctive grammar: 'would have', 'had X not happened', 'was X necessary/responsible for Y', blame/credit/regret attribution — needs abduction-action-prediction.
- Explicit demand to separate correlation from causation, or data given as correlations/(in)dependencies with a 'does A cause B?' question — needs causal-discovery / equivalence-class reasoning.
- Confounding or selection-bias cues: a lurking common cause, Simpson's-paradox-shaped aggregated data, observational (not experimental) evidence.
- Graded uncertainty markers: probabilities, base rates, likelihoods, 'how likely/confident', diagnostic test accuracy, false-positive rates — needs Bayesian posterior, not a point guess.
- Sequential/streaming evidence where a belief must be revised as new data arrives ('update your estimate given…').
- Risk of base-rate neglect: a vivid specific cue competing with a rare prior (medical diagnosis, fraud detection, rare-event screening).
- World-model 'what happens next if I change one thing' simulation requests where holding the rest of the system fixed matters.
- Arithmetic-heavy probabilistic problems where the model should offload to a probabilistic program / Bayesian network / code rather than reason in-head.

**Mode operators**

- **Climb the Causal Ladder** *(causal)* — trigger: The question is not 'what tends to co-occur' but 'what happens if I DO X' or 'what would have happened if X had been different'. Signals: the words intervene/do/force/set, policy or treatment effects, 'would', 'had', distinguishing correlation from causation. Pattern-matching on observed co-occurrence gives the wrong answer here.
  - protocol: 1. Classify the query into Pearl's rung: Rung 1 Association (P(Y|X), seeing), Rung 2 Intervention (P(Y|do(X)), acting), or Rung 3 Counterfactual (Y_x given observed evidence, imagining). 2. State the causal structure explicitly: list variables and the assumed causal graph (who points to whom), including confounders. 3. For Rung 2: mutilate the graph — sever incoming edges to the intervened variable, then propagate. Block back-door paths / adjust for confounders rather than conditioning naively. 4. For Rung 3: do not answer from association. 5. Translate the verbal query into the formal estimand BEFORE computing, then map back to natural language. 6. Flag when the answer is non-identifiable from available data.
  - grounding: CLadder: Assessing Causal Reasoning in Language Models (2312.04350) — CausalCoT formalize-then-solve over the three rungs.
- **Counterfactual Simulation (Abduction-Action-Prediction)** *(counterfactual)* — trigger: A 'what if it had been different' / 'was X necessary for Y' / blame-attribution / regret question where you must reconcile a counterfactual antecedent with already-observed facts. Distinct from forward prediction because the world's history is fixed and known.
  - protocol: 1. Abduction: from the observed outcome, infer the latent background variables (exogenous noise / unobserved causes) that must have held for what actually happened. 2. Action: apply the hypothetical intervention to the model — set the antecedent variable to its counterfactual value while KEEPING the abducted background fixed. 3. Prediction: propagate forward through the structural equations to read off the counterfactual outcome. 4. Handle the counterfactual type explicitly — single (basic), simultaneous (joint), sequential (nested), or under observed conditions (conditional). 5. Allow backtracking: if a downstream value contradicts a fixed observation, revisit the abduction step. 6. Contrast the counterfactual outcome with the factual one to answer necessity/sufficiency.
  - grounding: CounterBench (2502.11008) counterfactual types + CoIn search-with-backtracking; abduction-action-prediction structure from CLadder (2312.04350).
- **Causal Discovery from Statistical Evidence** *(inductive)* — trigger: You are handed correlations / (in)dependence facts / observational data and asked which causal structure produced them — 'does A cause B, or is it a common cause?'. The risk is leaping from correlation to a memorized causal story instead of deducing the admissible graph(s).
  - protocol: 1. Extract the full set of (conditional) independence and dependence relations stated or observed. 2. Apply causal-discovery constraints (e.g., PC-style rules): a v-structure A->C<-B is implied when A,B are marginally independent but dependent given C; chains/forks are ruled in or out by which conditionings break dependence. 3. Enumerate the Markov equivalence class — all DAGs consistent with the evidence — rather than committing to one. 4. Only assert a directed causal claim if it holds across the entire equivalence class; otherwise return 'underdetermined' and name what extra intervention would disambiguate. 5. Do not import prior world-knowledge about the variable names; reason from the statistical pattern alone, then optionally cross-check against domain priors.
  - grounding: Can Large Language Models Infer Causation from Correlation? / Corr2Cause (2306.05836) — pure causal inference from correlational statements.
- **Bayesian Belief Updating Under Uncertainty** *(probabilistic)* — trigger: Evidence arrives incrementally, beliefs are graded (probabilities, base rates, likelihoods, 'how confident…'), or the text contains explicit/qualitative uncertainty. Signals: base-rate problems, diagnostic reasoning, updating an estimate after new data, calibration. Naive pattern-matching ignores priors and over-weights the latest evidence.
  - protocol: 1. Identify the hypothesis space and assign an explicit prior P(H) — anchor on the base rate, not the vividness of the evidence. 2. For each new datum, write the likelihood P(E|H) for every hypothesis. 3. Update multiplicatively: posterior ∝ prior × likelihood, then normalize across hypotheses; iterate as evidence streams in (today's posterior is tomorrow's prior). 4. When arithmetic is load-bearing, OFFLOAD the computation: translate the verbal problem into a small Bayesian network / probabilistic program / Python snippet and execute it rather than estimating in-head. 5. Report a calibrated posterior distribution, not a point guess; surface how sensitive it is to the prior. 6. Sanity-check against the normative Bayesian answer; flag base-rate neglect or confirmation bias.
  - grounding: Bayesian Teaching Enables Probabilistic Reasoning in LLMs (2503.17523) for normative belief-updating; Reasoning over Uncertain Text / BLInD (2402.09614) for formal-mapping offload.

**Papers**

- ✅ [CLadder: Assessing Causal Reasoning in Language Models](https://arxiv.org/abs/2312.04350) — *Zhijing Jin, Yuen Chen, Felix Leeb, Luigi Gresele, Ojasv Kamal, Zhiheng Lyu, Kevin Blin, Fernando Gonzalez, Max Kleiman-Weiner, Mrinmaya Sachan, Bernhard Schölkopf* (2023, arXiv:2312.04350)  
  **Finding.** Introduces a 10k-question benchmark whose answers come from an oracle causal-inference engine, spanning Pearl's three rungs (association, intervention, counterfactual). Formal causal reasoning is very hard for LLMs; the proposed CausalCoT prompting strategy — formalize the query into the causal graph and estimand, then solve — substantially helps, showing the gain comes from explicit structure, not pattern recall.  
  **Grounds.** Grounds the 'Climb the Causal Ladder' operator: classify rung, externalize the causal graph, apply the do-operator/back-door adjustment before answering.  
  *Verified via WebFetch arxiv.org/abs/2312.04350.*
- ✅ [Can Large Language Models Infer Causation from Correlation?](https://arxiv.org/abs/2306.05836) — *Zhijing Jin, Jiarui Liu, Zhiheng Lyu, Spencer Poff, Mrinmaya Sachan, Rada Mihalcea, Mona Diab, Bernhard Schölkopf* (2023, arXiv:2306.05836)  
  **Finding.** Builds Corr2Cause (~200k examples) testing pure causal discovery: from correlational/independence statements, decide if a causal claim is valid. SOTA LLMs (GPT-4 F1 ~29) barely beat random and collapse out-of-distribution when variable names are perturbed — they pattern-match memorized causal facts rather than deducing the graph.  
  **Grounds.** Grounds the 'Causal Discovery from Statistical Evidence' operator: derive the Markov equivalence class from (in)dependence relations rather than guessing direction.  
  *Verified via WebFetch arxiv.org/abs/2306.05836.*
- ✅ [CounterBench: A Benchmark for Counterfactual Reasoning in Large Language Models](https://arxiv.org/abs/2502.11008) — *Yuefei Chen, Vivek K. Singh, Jing Ma, Ruixiang Tang* (2025, arXiv:2502.11008)  
  **Finding.** A 1,000-question counterfactual benchmark over diverse causal graphs and four question types (basic, joint, nested, conditional). Most LLMs score near-random (~50%) and even CausalCoT is limited; the proposed CoIn method — iterative causal-info extraction with search and backtracking — pushes top models past 90%, showing counterfactuals need an explicit structured procedure.  
  **Grounds.** Grounds the 'Counterfactual Simulation' operator: the abduction-action-prediction loop with backtracking and explicit counterfactual-type handling.  
  *Verified via WebFetch arxiv.org/abs/2502.11008.*
- ✅ [Bayesian Teaching Enables Probabilistic Reasoning in Large Language Models](https://arxiv.org/abs/2503.17523) — *Linlu Qiu, Fei Sha, Kelsey Allen, Yoon Kim, Tal Linzen, Sjoerd van Steenkiste* (2025, arXiv:2503.17523)  
  **Finding.** Shows untuned LLMs fall far short of normative Bayesian belief-updating, but training them to mimic a Bayesian model's predictions dramatically improves belief updating and the skill generalizes to new domains (e.g., inferring user preferences). Demonstrates Bayesian updating is a learnable, transferable reasoning strategy rather than native to LLMs.  
  **Grounds.** Grounds the 'Bayesian Belief Updating Under Uncertainty' operator: prior × likelihood → normalized posterior, iterated as evidence arrives, benchmarked against the normative answer.  
  *Verified via WebFetch arxiv.org/abs/2503.17523.*
- ✅ [Reasoning over Uncertain Text by Generative Large Language Models (BLInD)](https://arxiv.org/abs/2402.09614) — *Aliakbar Nafar, Kristen Brent Venable, Parisa Kordjamshidi* (2024, arXiv:2402.09614)  
  **Finding.** Introduces BLInD (Bayesian Linguistic Inference Dataset) to test probabilistic reasoning over text with explicit probabilities. LLMs struggle natively, but mapping the problem into formal frameworks — Python code, probabilistic algorithms, or probabilistic logic programming — and executing it markedly improves accuracy, transferring even to adapted causal datasets.  
  **Grounds.** Grounds the offload step of the Bayesian operator: translate uncertain-text problems into an executable Bayesian network / probabilistic program instead of estimating in-head.  
  *Verified via WebFetch arxiv.org/abs/2402.09614.*


## Analogical, case-based & first-principles reasoning

**Routing signals — when this family of thinking is needed**

- Problem framed as 'this is like/similar to/reminds me of X' or asks to apply a known solution to a new setting (analogical / case-based transfer).
- A novel-looking task with no provided worked example, but plausibly a member of a familiar problem class — route to Analogical Exemplar Recall.
- Detail-heavy or numeric question where surface details mislead, or where a governing law/definition/first principle should drive the answer ('why', 'derive', 'from first principles') — route to Step-Back Re-Derivation.
- Robustness pressure: distractors, perturbed values, or out-of-distribution variants of a known template — abstract-scaffold first.
- Repeated/experience-driven decisions with an accessible memory of past episodes (agent loops, support tickets, planning) — route to the CBR Retrieve-Reuse-Revise-Retain loop.
- Need to explain or solve in an unfamiliar domain by borrowing structure from a well-understood source domain — route to Cross-Domain Structure Mapping.
- Multi-step reasoning where from-scratch derivation is accumulating errors and analogous sub-problems exist (reuse their solutions instead).
- Far-transfer or counterfactual framing — engage analogical mapping but flag brittleness and verify projected inferences rather than trusting them.

**Mode operators**

- **Analogical Exemplar Recall** *(analogical)* — trigger: A novel problem with no given worked example, but which resembles a class of problems the solver has likely seen; you are about to reason from a blank slate on something that is probably not actually new.
  - protocol: 1. Before solving, ask 'what 2-3 problems do I already know how to solve that share this one's deep structure?'. 2. Self-generate those analogues WITH their worked solutions/relevant principles. 3. Extract the transferable solution schema (the move set), discarding surface specifics. 4. Map the schema's roles onto the target's entities. 5. Solve the target via the mapped schema; if the analogues disagree, prefer the closest structural match.
  - grounding: Large Language Models as Analogical Reasoners (arXiv:2310.01714)
- **Step-Back First-Principles Re-Derivation** *(inductive)* — trigger: A question dense with specific details/values where surface pattern-matching is misleading or brittle, or where the answer should follow from a known law/definition/principle; also when distractors or perturbed numbers threaten robustness.
  - protocol: 1. Strip the instance to its abstract form (replace concrete values with variables, name the underlying concept). 2. Pose the 'step-back' question: what general principle, law, or definition governs this class? 3. State that principle explicitly. 4. Deduce the answer by instantiating the principle on the concrete details. 5. Sanity-check that the concrete answer is consistent with the abstract derivation (re-substitute values).
  - grounding: Take a Step Back: Evoking Reasoning via Abstraction (arXiv:2310.06117); AbstRaL (arXiv:2506.07751)
- **Case-Based Retrieve–Reuse–Revise–Retain Loop** *(analogical)* — trigger: Recurring or experience-driven tasks where a memory of prior solved episodes exists or can accumulate (agents, decision-making, support, planning); when re-deriving each instance from scratch wastes effort or accumulates errors.
  - protocol: 1. RETRIEVE: index the new problem and pull the most structurally-similar past case(s) from case memory. 2. REUSE: lift the retrieved solution/plan as a draft. 3. REVISE: adapt it to the differences between old and new case; verify the adapted solution. 4. RETAIN: store the new (problem, revised-solution, outcome) as a fresh case for future retrieval. Maintain similarity metrics on deep structure, not surface tokens.
  - grounding: Review of Case-Based Reasoning for LLM Agents (arXiv:2504.06943); Thought Propagation (arXiv:2310.03965)
- **Cross-Domain Structure Mapping** *(analogical)* — trigger: An unfamiliar/under-specified target domain where a richer, better-understood source domain shares relational structure; need to import explanatory or solution structure across a domain boundary (far transfer).
  - protocol: 1. Build a relational schema of the source (objects + the relations/causal links among them), ignoring surface attributes. 2. Find a one-to-one correspondence between source roles and target roles by aligning relations, not features. 3. Project unmapped source relations as candidate inferences about the target. 4. Stress-test transfer: check each projected inference against target constraints; explicitly flag where the analogy breaks (the alignment is partial or the far-transfer mapping fails) and bound conclusions accordingly.
  - grounding: Emergent Analogical Reasoning in Large Language Models (arXiv:2212.09196)

**Papers**

- ✅ [Large Language Models as Analogical Reasoners](https://arxiv.org/abs/2310.01714) — *Michihiro Yasunaga, Xinyun Chen, Yujia Li, Panupong Pasupat, Jure Leskovec, Percy Liang, Ed H. Chi, Denny Zhou* (2023, arXiv:2310.01714)  
  **Finding.** Analogical Prompting has the model SELF-GENERATE relevant exemplars and high-level knowledge before solving, rather than retrieving or hand-labeling few-shot examples. This self-recall of analogous solved problems beats 0-shot CoT and manual few-shot CoT on math (GSM8K, MATH), code generation, and BIG-Bench reasoning, while adapting the exemplars to each specific problem.  
  **Grounds.** Grounds the 'analogical exemplar self-generation' operator — solve-by-analogy by recalling/synthesizing your own structurally similar cases before attacking the target.  
  *Verified via arxiv id_list API.*
- ✅ [Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models](https://arxiv.org/abs/2310.06117) — *Huaixiu Steven Zheng, Swaroop Mishra, Xinyun Chen, Heng-Tze Cheng, Ed H. Chi, Quoc V. Le, Denny Zhou* (2023, arXiv:2310.06117)  
  **Finding.** Step-Back Prompting first abstracts a concrete, detail-laden question into a higher-level concept or first principle (the 'step-back question'), then reasons from that principle back down to the answer. Gains: MMLU Physics/Chemistry +7%/+11%, TimeQA +27%, MuSiQue +7% on PaLM-2L; replicated on GPT-4 and Llama2-70B.  
  **Grounds.** Grounds the 'first-principles step-back abstraction' operator — re-derive from governing principles instead of pattern-matching surface details.  
  *Verified via arxiv id_list API.*
- ✅ [Thought Propagation: An Analogical Approach to Complex Reasoning with Large Language Models](https://arxiv.org/abs/2310.03965) — *Junchi Yu, Ran He, Rex Ying* (2023, arXiv:2310.03965)  
  **Finding.** Thought Propagation proposes a set of analogous problems related to the input, solves them, then REUSES their solutions/strategies to yield the target solution or a knowledge-intensive plan — countering error accumulation in from-scratch multi-step reasoning. Gains: +12% shortest-path, +13% creative-writing preference, +15% agent planning completion.  
  **Grounds.** Grounds the case-based 'reuse-and-revise' operator — transfer the solution structure of solved analogues rather than re-deriving each new instance.  
  *Verified via arxiv id_list API.*
- ✅ [Review of Case-Based Reasoning for LLM Agents: Theoretical Foundations, Architectural Components, and Cognitive Integration](https://arxiv.org/abs/2504.06943) — *Kostas Hatalis, Despina Christou, Vyshnavi Kondapalli* (2025, arXiv:2504.06943)  
  **Finding.** Systematizes the classic CBR Retrieve–Reuse–Revise–Retain cycle as an architecture for LLM agents: store past episodes as structured cases, retrieve by similarity to the new problem, adapt the retrieved solution, then retain the revised case — giving agents explicit, updatable experiential memory and a mathematical model of each stage.  
  **Grounds.** Grounds the full 'case-based reasoning loop' operator — the retrieve/adapt/retain machinery behind solving-by-prior-case and continual case accumulation.  
  *Verified via arxiv id_list API.*
- ✅ [Emergent Analogical Reasoning in Large Language Models](https://arxiv.org/abs/2212.09196) — *Taylor Webb, Keith J. Holyoak, Hongjing Lu* (2022, arXiv:2212.09196)  
  **Finding.** GPT-3 zero-shot matched or exceeded humans on Raven-style matrix analogies, letter-string analogies, and verbal/story analogies, showing emergent abstract relational pattern induction and cross-domain mapping — though later work shows this is brittle on counterfactual/far-transfer variants, defining the operator's failure surface.  
  **Grounds.** Grounds the 'cross-domain structure mapping' operator — align relational structure (not surface features) between a source and target domain; also flags where analogical transfer breaks (far transfer / counterfactual).  
  *Verified via arxiv id_list API.*
- ✅ [AbstRaL: Augmenting LLMs' Reasoning by Reinforcing Abstract Thinking](https://arxiv.org/abs/2506.07751) — *Silin Gao, Antoine Bosselut, Samy Bengio, Emmanuel Abbe* (2025, arXiv:2506.07751)  
  **Finding.** AbstRaL uses RL to teach models to first restate a problem as an abstract, symbol/variable-level pattern (decoupled from concrete surface values) and reason over that scaffold, which markedly improves robustness to distractors and value perturbations on GSM-style benchmarks versus reasoning on the concrete instance.  
  **Grounds.** Reinforces the 'abstract scaffold / first-principles re-derivation' operator with evidence that explicit abstraction improves out-of-distribution robustness, not just accuracy.  
  *Verified via arxiv id_list API.*


## Convergent reasoning, self-verification & dialectic

**Routing signals — when this family of thinking is needed**

- The task has a single verifiable correct answer (math, logic, factual QA) and a single greedy attempt is unreliable — route to Convergent Sampling-and-Vote.
- A draft already exists and the risk is fabricated/unsupported facts rather than missing information — route to Chain-of-Verification.
- The model expresses high confidence but the claim is checkable and the cost of being wrong is high — trigger independent verification before committing.
- Multiple plausible-but-conflicting answers or framings are on the table, or the first answer 'sounds right' on a contested question — route to Dialectic Debate.
- The answer depends on a long chain where one bad step is fatal (proofs, derivations, multi-step plans) — route to Stepwise Process Verification.
- You have N candidate solutions and must pick the best, not just the most frequent — use process-reward step scoring to select.
- Self-consistency vote share is split with no clear plurality — escalate from voting to debate or stepwise verification.
- The user explicitly asks to 'double-check', 'verify', 'are you sure', 'stress-test', 'find the flaw', or 'reach consensus' — direct cues for the verification/dialectic family.
- Phase transition from divergent generation to commitment: many candidates exist and the job is now to NARROW to one — this whole family (not divergent generation) is required.

**Mode operators**

- **Convergent Sampling-and-Vote** *(probabilistic / convergent)* — trigger: There is a single objectively correct answer but the path to it is error-prone, and one greedy chain is unreliable (math word problems, multi-hop QA, any task where a wrong intermediate step silently corrupts the result). Use when you can afford N samples and answers are comparable/aggregatable.
  - protocol: 1. Sample K independent reasoning paths at non-zero temperature (diverge on purpose). 2. Extract the final answer from each, normalizing to a canonical form so equivalent answers collide. 3. Marginalize over reasoning: tally answers and select the modal (majority-voted) one; for free-form outputs, cluster semantically then vote on clusters. 4. Report the vote share as a confidence signal; if no answer clears a plurality threshold, escalate (more samples, or switch to debate/verification). Convergence = many independent paths agreeing.
  - grounding: Self-Consistency Improves Chain of Thought Reasoning in Language Models (arXiv:2203.11171)
- **Chain-of-Verification (independent self-check)** *(metacognitive / deductive)* — trigger: A confident-sounding draft may contain fabricated facts or unsupported claims (longform generation, list/entity questions, factual summaries). Use when the failure mode is hallucination rather than search, and the draft can be decomposed into discrete checkable assertions.
  - protocol: 1. Produce a draft answer. 2. Enumerate the atomic factual claims in the draft and turn each into a standalone verification question. 3. CRITICAL: answer each verification question in a fresh context that does NOT see the draft, so the answer is not anchored to the original mistake. 4. Compare verification answers against the draft; flag contradictions. 5. Regenerate the final answer retaining only claims that survived verification. Optionally add a backward check: substitute the answer back as a premise and confirm it reconstructs the original givens.
  - grounding: Chain-of-Verification Reduces Hallucination in LLMs (arXiv:2309.11495); Large Language Models are Better Reasoners with Self-Verification (arXiv:2212.09561)
- **Dialectic Debate-to-Consensus** *(dialectical)* — trigger: The question is contestable, the first answer might be locally plausible but wrong, or a single perspective has a blind spot (strategic/commonsense reasoning, contested factual claims, decisions with competing valid framings). Use when independent viewpoints can meaningfully critique each other.
  - protocol: 1. Instantiate 2+ independent solvers; have each produce an answer and its justification (thesis / antithesis). 2. Run R rounds: in each, show every agent the others' answers and reasoning and ask it to critique them and revise its own. 3. Track convergence; stop when agents agree or after R rounds. 4. Synthesize the consensus answer (or the position that survived critique). Use a held-out judge to break residual ties. The mechanism is mutual cross-examination, not averaging.
  - grounding: Improving Factuality and Reasoning in Language Models through Multiagent Debate (arXiv:2305.14325)
- **Stepwise Process Verification & Selection** *(decompositional / deductive)* — trigger: A long multi-step derivation must be trusted, and a single bad step invalidates the whole chain (proofs, multi-step math, complex plans). Use when you have or can generate multiple candidate trajectories and need to pick the soundest, not just the most common.
  - protocol: 1. Require each reasoning step to explicitly state the premises it consumes (Natural Program style). 2. Verify each step in ISOLATION: give a checker only that step's premises and ask whether the conclusion deductively follows; reject chains with any non-entailed step. 3. When ranking multiple candidate solutions, score every step (process reward) rather than only the final answer, and select the trajectory whose weakest step scores highest. 4. Combine with vote: among process-valid candidates, take the consensus answer. Per-step verification is a stronger convergence signal than outcome-only checks.
  - grounding: Deductive Verification of Chain-of-Thought Reasoning (arXiv:2306.03872); Let's Verify Step by Step (arXiv:2305.20050)

**Papers**

- ✅ [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171) — *Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le, Ed Chi, Sharan Narang, Aakanksha Chowdhery, Denny Zhou* (2022, arXiv:2203.11171)  
  **Finding.** Replaces greedy decoding with: sample a diverse set of reasoning paths, then marginalize over them by taking the majority-voted final answer. Large gains (GSM8K +17.9%, SVAMP +11.0%, AQuA +12.2%, StrategyQA +6.4%) with no training. Exploits that correct reasoning converges on the same answer through many different paths while errors scatter.  
  **Grounds.** Grounds the convergent-sampling/vote operator: divergent generation followed by probabilistic marginalization to converge on the answer the most reasoning paths agree on.  
  *Verified via WebFetch arXiv API id_list=2203.11171.*
- ✅ [Chain-of-Verification Reduces Hallucination in Large Language Models](https://arxiv.org/abs/2309.11495) — *Shehzaad Dhuliawala, Mojtaba Komeili, Jing Xu, Roberta Raileanu, Xian Li, Asli Celikyilmaz, Jason Weston* (2023, arXiv:2309.11495)  
  **Finding.** CoVe pipeline: (1) draft an initial response, (2) plan verification questions that fact-check the draft, (3) answer those questions INDEPENDENTLY so answers are not biased by the original draft, (4) regenerate a final verified response. The independence of the verification questions is what removes errors. Decreases hallucination across list questions, closed-book QA, and longform generation.  
  **Grounds.** Grounds the self-verification / chain-of-verification operator: treat your own draft as a hypothesis, decompose it into checkable sub-questions, answer them independently, then revise.  
  *Verified via WebFetch arXiv API id_list=2309.11495.*
- ✅ [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325) — *Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, Igor Mordatch* (2023, arXiv:2305.14325)  
  **Finding.** Multiple independent model instances each propose an answer and reasoning, then over several rounds each agent reads the others' responses and revises its own toward a consensus. This thesis-antithesis-synthesis loop improves mathematical and strategic reasoning and reduces false answers and hallucinations versus a single chain of thought.  
  **Grounds.** Grounds the dialectic-debate operator: instantiate opposing/independent positions, force cross-critique over rounds, and converge on a synthesized consensus.  
  *Verified via WebFetch arXiv API id_list=2305.14325.*
- ✅ [Deductive Verification of Chain-of-Thought Reasoning](https://arxiv.org/abs/2306.03872) — *Zhan Ling, Yunhao Fang, Xuanlin Li, Zhiao Huang, Mingu Lee, Roland Memisevic, Hao Su* (2023, arXiv:2306.03872)  
  **Finding.** Introduces 'Natural Program', a format where each reasoning step explicitly lists the premises it depends on, then decomposes verification into step-by-step subprocesses that each receive ONLY their necessary premises and check whether that single step deductively follows. Isolating each step makes verification far more reliable and filters reasoning chains that look fluent but are not entailed.  
  **Grounds.** Grounds the stepwise deductive-verification operator: make premises explicit per step and check local entailment in isolation rather than judging the whole chain at once.  
  *Verified via WebFetch arXiv API id_list=2306.03872.*
- ✅ [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) — *Hunter Lightman, Vineet Kosaraju, Yura Burda, Harri Edwards, Bowen Baker, Teddy Lee, Jan Leike, John Schulman, Ilya Sutskever, Karl Cobbe* (2023, arXiv:2305.20050)  
  **Finding.** Process supervision (a reward model scoring each intermediate step, PRM) substantially beats outcome supervision (scoring only the final answer) for selecting correct solutions; the PRM-ranked best-of-N solves 78% of a MATH subset. Released PRM800K, 800K step-level human labels. Establishes per-step verification as the stronger convergence signal.  
  **Grounds.** Grounds the process-reward-verification operator: score every step of every candidate and converge by selecting the trajectory whose weakest step is strongest, not just by final-answer voting.  
  *Verified via WebFetch arXiv API id_list=2305.20050.*
- ✅ [Large Language Models are Better Reasoners with Self-Verification](https://arxiv.org/abs/2212.09561) — *Yixuan Weng, Minjun Zhu, Fei Xia, Bin Li, Shizhu He, Shengping Liu, Bin Sun, Kang Liu, Jun Zhao* (2022, arXiv:2212.09561)  
  **Finding.** Backward self-verification: take the CoT-derived answer, substitute it back as a given condition, mask an original premise, and ask the model to re-derive the masked value; candidates that reproduce the original conditions score higher. Produces interpretable validation scores to rank candidate answers, improving arithmetic, commonsense and logical reasoning.  
  **Grounds.** Grounds the backward-consistency-check operator: verify a candidate answer by reversing the inference and checking it reconstructs the original givens.  
  *Verified via WebFetch arXiv API id_list=2212.09561.*
