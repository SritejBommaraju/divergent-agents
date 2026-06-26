# LLM-driven evolution & program/idea search

*LLM-driven evolution & program/idea search*

[← back to master report](../REPORT.md)

## Key takeaways

- Novelty comes from the OUTER LOOP, not a single forward pass: every method here gets superhuman/novel results by sampling many LLM variants and applying hard selection — the LLM is the variation operator, an external evaluator is the truth signal. The agent's job is to generate many candidates cheaply and let a scorer decide.
- A reliable, automatable fitness function is the precondition. FunSearch, Eureka, EoH, and AlphaEvolve all work only because the domain has a fast programmatic evaluator. Before evolving, build/define the scorer; without it the loop has no direction and mode-collapse returns.
- Explicitly demand difference. EoH's strongest operator literally instructs the model to produce a heuristic 'totally different' from prior ones; LMX and ELM diversify via parents/niches. Telling the model to diverge — and giving it the prior attempts to diverge FROM — is more effective than hoping temperature alone produces novelty.
- Quality-DIVERSITY beats pure quality for discovery. MAP-Elites (ELM) and island models (FunSearch) keep many distinct good solutions in different behavioral niches, preventing premature convergence. Optimizing only the single best score collapses the search; maintaining a diverse archive sustains exploration.
- Memory of past attempts turns one inference into a search step. OPRO (score-sorted trajectory), Eureka (reward reflection), and AlphaEvolve (program database in-context) all feed the history of attempts-and-outcomes back into the prompt, letting the model infer the improvement direction rather than restart from its prior mean.
- Separate idea-space from implementation-space. EoH co-evolves a natural-language 'thought' plus code; reasoning about WHICH idea is novel in language, then implementing it, yields more divergent solutions than mutating code diffs directly.
- Meta-evolution compounds gains. Promptbreeder evolves its own mutation operators; AlphaEvolve mixes an ensemble of models/settings. Diversifying HOW you mutate — not just what you mutate — keeps the search productive over long horizons.

## Harness mechanisms

- Evolve-mode skill: given a problem + a runnable scorer, maintain a persistent archive of top-k candidate programs; each generation, build a best-shot prompt (2-3 prior solutions sorted worst→best) and ask Claude for a strictly-better variant; accept only if it beats the archive. The FunSearch/AlphaEvolve core loop as a reusable Claude Code command.
- Island/archive persistence on disk: run several independent archives ('islands') that occasionally reseed from the global best, so different runs explore different algorithmic families and resist mode collapse over long sessions.
- MAP-Elites behavioral grid: define 2-3 descriptors (code size, algorithm family, dependency count, time complexity class), bin every candidate, keep the best per cell, and seed new mutations from deliberately diverse cells — surfacing unconventional but viable solutions the top-1 search would discard.
- Operator library with named mutation prompts: implement EoH's E1/E2/M1/M2/M3 plus Promptbreeder thinking-styles as a rotating set; alternate novelty-seeking ('design something provably different from all prior attempts') with refinement operators on a schedule, and log which operator produced each score gain.
- Reflection channel: have the evaluator emit component-level telemetry, auto-summarize it into a textual critique (Eureka-style), and feed that — not just the scalar score — into the next generation's prompt so edits are targeted rather than random.
- LMX crossover tool: select 3-5 high-fitness, mutually-distinct parents (one per archive niche), present them as unlabeled few-shot examples, and ask Claude for 'another in the same spirit' to recombine their features.
- OPRO ledger wrapper: a lightweight decorator around any agent step with a numeric objective that injects a score-sorted history of past attempts into the prompt and requests a candidate expected to beat them all — cheap memory-as-search add-on.
- Meta-mutation step: periodically ask Claude to invent NEW mutation operators based on which past operators yielded improvements (Promptbreeder self-reference), and persist the evolving operator set across sessions.
- Evaluator cascade: gate expensive full benchmarks behind fast smoke tests so many candidates can be screened in parallel/background (AlphaEvolve), maximizing the number of LLM variants the loop can afford to try per unit time.

## Papers

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
