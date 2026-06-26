# Quality-Diversity, Novelty Search & open-endedness

*Quality-Diversity, Novelty Search & open-endedness*

[← back to master report](../REPORT.md)

## Key takeaways

- Objectives are deceptive: directly maximizing the target metric reliably traps search in local optima; rewarding behavioral NOVELTY (distance from an archive of past behaviors) discovers the stepping stones that actually reach hard goals (Novelty Search). This is the core license for an agent to not always pick the modal next token/move.
- Keep an ARCHIVE, not a single best. MAP-Elites' central move — bin solutions by human-chosen behavior dimensions and keep the best per bin — turns 'find the answer' into 'illuminate the space of qualitatively different good answers,' guaranteeing coverage and breaking mode collapse.
- Pure novelty is necessary but not sufficient: most novel things are trivial. A foundation model can supply human-aligned TASTE (OMNI's 'model of interestingness') to steer divergence toward novelty that is both feasible and worthwhile — the crucial filter between mode-collapse and useless wandering.
- LLMs are far more valuable as DIVERSITY ENGINES inside a QD loop than as one-shot answerers: ELM uses the LLM as an intelligent mutation operator, QDAIF uses it as both variation generator and natural-language quality/diversity judge, FunSearch uses it to mutate programs across an island archive. The pattern is: LLM proposes variation, an archive enforces diversity, an evaluator enforces quality.
- AI feedback unlocks QD for fuzzy domains. You don't need a numeric fitness function — you can ask the model in plain language 'how good is this?' and 'how different is this from these others?' (QDAIF/QDHF), making novelty search usable for writing, design, and research ideation where no metric exists.
- Stepping-stones come from cross-pollination and self-generated curricula: POET transfers solutions between sibling problems; OMNI-EPIC and POET invent their own increasingly diverse, learnable-yet-interesting problems and retain BOTH successes and informative failures in the archive.
- Exploration beats greedy trajectories on hard tasks: Intelligent Go-Explore keeps an archive of reached states and uses model taste to decide where to RETURN and branch from, beating Reflexion-style single-trajectory agents exactly where forward-only reasoning gets stuck.
- The whole lineage now reaches coding agents directly (ELM, FunSearch, OMNI-EPIC, Darwin Godel Machine), so 'archive + novelty + interestingness gate + LLM mutation' is a concrete, proven blueprint for a divergent coding harness, not just an RL/robotics idea.

## Harness mechanisms

- Behavior-characterization + novelty archive: after generating each candidate solution, have the agent emit a compact behavior descriptor (approach-tags or an embedding), store it, and score new candidates by k-NN distance to the archive. Select the most-novel-yet-viable candidate instead of the modal one. A '/diverge' skill could force N candidates, embed, and rank by novelty.
- MAP-Elites grid skill: ask for (or infer) 2-3 axes of variation for the task (e.g. paradigm x dependency-footprint x complexity for code; tone x structure x length for writing), maintain a literal grid file, bin each generated candidate, keep only per-cell elites, and surface empty cells as explicit generation prompts ('produce a functional, zero-dependency variant') to force coverage.
- LLM-as-interestingness gate (OMNI): before committing effort to a direction, prompt the model to rate it on feasibility (learnable now) AND interestingness (novel vs an explicit log of already-tried approaches, and worthwhile). Only pursue directions that clear both, preventing both mode-collapse and trivial wandering.
- LLM-as-mutation-operator loop (ELM/FunSearch): keep an archive/'islands' of working solutions; each iteration sample an elite, instruct the agent to mutate it in a NAMED direction (swap algorithm/data structure/tradeoff), evaluate with tests, and re-bin. Use best-shot island prompting (show the current best variants as context) to bootstrap increasingly novel-yet-correct solutions.
- AI-feedback QD for fuzzy tasks (QDAIF/QDHF): for writing/design/ideation, define diversity axes in natural language and use the model itself to (a) propose variants pushing toward under-filled regions and (b) score quality and pairwise distance-from-archive via rubric prompts — yielding a covered creative space instead of one safe draft.
- Go-Explore-style state archive with backtracking (IGE): give the agent an explicit archive of promising partial states (repo snapshots, plan branches, reasoning frontiers); each step the model scores which archived state is most interesting to RESUME from, returns there, explores a few actions, and flags serendipitous results to archive — converting a linear agent into a tree explorer that can back up instead of tunnel-visioning the first path.
- Self-curriculum / stepping-stone generator (POET/OMNI-EPIC): maintain a code-defined archive of solved and attempted tasks; an LLM proposes the next task as an executable spec/test that is just-beyond-current-ability and novel vs the archive; retain informative FAILURES as stepping stones. Periodically attempt transferring the current best solution onto a sibling open sub-problem (POET transfer) to unlock stalled progress.
- Explicit anti-mode-collapse selection step: institutionalize a rule that the agent must generate multiple genuinely distinct candidates (verified distinct by an AI-feedback diversity check) before converging, and must justify the chosen one against the alternatives — making divergence a required phase of the loop rather than an afterthought.

## Papers

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
