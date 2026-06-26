# Research-idea generation & autonomous scientific discovery

*Research-idea generation & autonomous scientific discovery*

[← back to master report](../REPORT.md)

## Key takeaways

- Over-generate-then-rank is the single most validated novelty mechanism: the Stanford 100+ researcher study (2409.04109) got expert-judged super-human novelty by sampling thousands of candidates and ranking, NOT from one strong sample. Divergence is a search/selection problem, not a single-prediction problem.
- Diversity collapses with scale unless knowledge inflow is actively managed: both the Stanford study (rising duplicate rate) and Nova (2410.14255) show that raw resampling plateaus into repetition; deliberately planning what NEW external knowledge to retrieve each round is what produced 3.4x more unique novel ideas.
- Novelty without grounding is a mirage: the Ideation-Execution Gap (2506.20803) found the LLM novelty advantage largely vanishes after 100+ hours of real execution. Any harness that diverges must re-validate ideas against feasibility/execution, not trust ideation-stage novelty scores.
- LLM self-evaluation of its own novelty is unreliable (Stanford study): the generator must not be the judge. Use a separate critic/ranker with an explicit rubric, ideally calibrated against human judgments (SciMuse 2405.17044 shows interestingness is learnable/predictable).
- Structural recombination beats free association for non-obvious ideas: SciAgents (2409.05556) and ResearchAgent (2404.07738) force connections across distant knowledge-graph nodes/entities, surfacing interdisciplinary links the LLM would never reach by following its highest-probability associations.
- Search with backtracking outperforms single-pass planning for genuine discovery: AI Scientist-v2 (2504.08066) uses agentic tree search with explicit branch evaluation and abandonment to produce a peer-review-passing paper — the agent must be willing to discard its first plan.
- Structured, multi-dimensional critique steers the novelty-validity frontier: MOOSE's past/present/future feedback (2309.02726) and ResearchAgent's role-specialized reviewers give explicit dials to avoid both 'too safe/obvious' and 'novel but invalid.'

## Harness mechanisms

- Over-generate-and-rank skill: sample N candidate approaches at high temperature (each seeded by a distinct retrieval), dedup via embedding cosine, then rank with a SEPARATE novelty-only LLM judge; auto-stop when marginal unique-idea yield drops (operationalizes 2409.04109's quantity-vs-duplication finding).
- Active-retrieval diversity loop (Nova-style): before each idea batch the agent must name a knowledge gap and issue a targeted search/codebase query, conditioning the next batch only on freshly retrieved material; maintain a diversity ledger steering toward under-explored regions.
- Survives-grounding gate (Ideation-Execution Gap): no divergent idea is promoted until a cheap execution probe (failing test, tiny prototype, sanity calc) runs; re-score novelty AND feasibility post-probe and drop ideas whose appeal collapses on contact with reality.
- Random-path provocation over a concept graph (SciAgents/ResearchAgent): build a lightweight graph from repo symbols/domain/literature, sample distant node pairs, and require the agent to invent a mechanism bridging them — structurally forcing non-obvious recombination.
- Agentic tree search with an LLM-critic heuristic (AI Scientist-v2): represent approaches as a tree, expand best-first using a reviewer subagent's novelty+soundness score, and keep a backtracking stack so the agent abandons dead branches instead of committing to its first plan.
- Three-feedback self-refinement template (MOOSE): wrap drafts in past-feedback (is it obvious/known? push novelty), present-feedback (consistent with current evidence/tests? push validity), future-feedback (does it open follow-on work?), looping until both novelty and validity thresholds pass.
- Decoupled generator/judge with role-specialized reviewers (ResearchAgent): never let the generating context score itself; run N critic subagents each owning one rubric dimension (novelty, validity, clarity, feasibility) returning structured critiques the generator must resolve.
- Personalized interestingness ranker (SciMuse): condition generation on the specific user's/project's concept neighborhood and rank candidates with an LLM scorer calibrated to predict expert interest, using graph-bridging features as a selection heuristic so divergence stays targeted and relevant.

## Papers

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
