# Analogical, lateral & conceptual-blending reasoning

*Analogical, lateral & conceptual-blending reasoning*

[← back to master report](../REPORT.md)

## Key takeaways

- Divergence is a two-phase move, not one prompt: first lift the problem OUT of its surface form (step-back abstraction, structured/schema representation), then transfer or recombine at that higher level, then descend back to a concrete, coherent answer. Token-level continuation is precisely what anchors a model to the obvious; the structured/abstract layer is where non-obvious combinations become reachable.
- Self-generated analogs beat fixed exemplars: making the model recall and solve its OWN analogous problems (Analogical Prompting, Thought Propagation) conditions the answer on relational structure rather than the most-likely next token — and solving the analogs FIRST prevents premature convergence on the target's greedy path.
- Semantic distance is the tunable diversity knob (Serendipity by Design): the creative payoff of a cross-domain seed grows the more remote the source is. Random nearby seeds barely help; deliberately MAXIMALLY-distant seeds with an enforced mapping do.
- Cross-domain prompts help LLMs less than humans by default — the model needs the mapping FORCED and the source DISTANT, otherwise it collapses back to in-distribution ideas. Optionality kills it; the transfer must be a required, cited step.
- Conceptual blending needs an explicit bridge: novelty-that-is-grounded comes from finding the connecting concept between two input spaces (PopBlends) and recombining structured slots (Cooking Up Creativity), not from blending raw text.
- Lateral thinking is elicited by interactive hypothesis-probing under incomplete information (Weak-eval-Strong): forcing the model to ask falsifying questions before answering surfaces alternatives a one-shot completion skips.
- You must measure divergence to trust it: originality/flexibility/fluency gated by feasibility/clarity (LiveIdeaBench) distinguishes 'genuinely novel and usable' from 'merely different,' and watch for flexibility-collapse / homogenization as the failure mode of LLM-assisted ideation.

## Harness mechanisms

- Mandatory step-back gate: block concrete edits/answers until the agent records (a) the abstract problem class, (b) 2-3 principle-level solution families for that class. Forces breadth before the first commit (from Take a Step Back).
- Analogize-first pre-step: require the agent to self-generate N structurally-analogous problems from DIFFERENT domains, state each one's core trick, then implement by explicitly mapping the chosen trick and citing it (from Analogical Reasoners + Thought Propagation).
- Distant-seed injector: maintain an embedded corpus of domains/objects; each ideation round, sample the source MAXIMALLY far from the task domain and require a property-mapping from it. Expose semantic distance as a CLI dial and auto-escalate distance until coherence breaks (from Serendipity by Design).
- Schema crossover engine: decompose every candidate into slots (goal/mechanism/constraint/medium/failure-mode), swap slots across semantically distant candidates, back-translate the recombined schema to a concrete proposal. A genetic-style recombination over structured representations (from Cooking Up Creativity).
- Blend skill: given task domain + a forced unrelated domain, run PopBlends stages (attributes of each space -> bridging concept -> blended artifact -> coherence prune) to import a foreign mechanism into the solution (from PopBlends).
- Falsify-your-first-answer loop: before committing, the agent must ask 5 questions that would rule out its initial/obvious interpretation, answered by a judge subagent holding hidden spec details (from Weak-eval-Strong).
- Diverge-then-converge with a creativity judge: generate a wide candidate set, score each on originality/flexibility/feasibility/clarity, keep the Pareto front (high originality AND feasibility), and reject if the set collapses into one category (homogenization detector) (from LiveIdeaBench).
- Parallel-analog fan-out: spawn k subagents each solving a deliberately different analog of the task, then a synthesis agent must inherit at least one non-obvious move from each analog into the final design (from Thought Propagation).

## Papers

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
