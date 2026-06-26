# Structured reasoning & search at inference time

*Structured reasoning & search at inference time*

[← back to master report](../REPORT.md)

## Key takeaways

- The single greedy chain is the core failure mode; every method here replaces 'commit to most-likely next token/step' with generate-many + evaluate + select/backtrack.
- Divergence has three distinct levers: (1) sample width — diverse paths (self-consistency, best-of-N); (2) structure — branch with backtracking (ToT) or recombine across branches (GoT); (3) depth — sequential self-revision of one line (R1-style, Snell's revision axis).
- Search is only as good as the selector. A verifier / value function (PRM, LM self-eval, or real test feedback) is what converts many candidates into a better answer — without it, wide sampling just adds noise.
- Ground the reward in external signals when possible. LATS and coding agents get reliable rewards from running tests/builds; pure self-evaluation (ToT/GoT) is weaker and can confidently mis-rank — prefer executable verification over LM opinion.
- Compute allocation should be difficulty-aware (Snell): easy tasks -> deepen one chain via revision; hard tasks -> widen the search. Always-on fixed best-of-N wastes budget on easy work and under-searches hard work.
- Failed branches are information, not waste (Reflexion): a structured 'why it failed, so try a different axis' note enforces genuine diversity across retries instead of re-sampling near the same wrong attempt.
- Recombination, not just branching, produces novelty (GoT): merging the best parts of independent solution branches yields answers no single chain reaches.
- The newest models (R1) can perform explore/verify/backtrack in-context, so a harness can often elicit deliberate search via scaffolding prompts and only escalate to external tree machinery for the hardest problems.

## Harness mechanisms

- Branch-and-verify skill: at any high-stakes decision (architecture, root-cause, fix strategy), fan out k parallel sub-agents at elevated temperature, score each candidate with a verifier sub-agent grounded in real tests/build, and keep a frontier of top-b — the explicit ToT/best-of-N loop for code.
- Persistent search-tree state file (JSON/markdown): store the frontier, each node's candidate edit, eval score, and reflection, so backtracking and explore/exploit decisions survive context resets and the agent can pop back to an abandoned-but-promising branch.
- Difficulty router (Snell-inspired): a cheap pre-step rates task hardness and chooses strategy — single chain + sequential self-revision for easy tasks, wide MCTS/best-of-N for hard ones — with an explicit compute budget the controller spends where marginal gain is highest.
- MCTS-over-tools loop (LATS): nodes = repo states, expansions = candidate commands/edits, reward = actual test/build/lint outcomes backpropagated, selection via UCB (LM value + exploration bonus for under-tried branches) to ground search in real feedback rather than self-judgment.
- Diversity-enforcing retry wrapper (Reflexion): on verification failure, force a structured reflection note and require the next attempt to differ in approach from all prior attempts, using the reflection log as the explicit anti-duplication constraint.
- Merge/aggregate operation (GoT): after exploring 2-3 independent branches, run a synthesis step that extracts the best component from each into a hybrid solution, plus a refine-loop edge that iterates critique->improve until a quality bar is met.
- Step-level verifier sub-agent (PRM): a reusable scoring function that emits per-step pass/fail + aggregate score for any plan or patch, used both to rank best-of-N outputs and to prune weak partial branches mid-search, with step scores tied to concrete checks (typecheck, spec match, invariant preservation).
- Inline deliberation prompt template (R1): for planning phases, require 'enumerate >=3 distinct approaches, red-team each, choose, then verify against constraints before any edit' with a long-thinking budget — cheap divergence that precedes external search machinery.

## Papers

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
