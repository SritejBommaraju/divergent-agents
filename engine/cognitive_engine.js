/*
 * cognitive_engine.js — the Cognitive Engine (run with the Workflow tool).
 *
 * v2 of the Divergence Engine. Instead of ALWAYS doing divergent brainstorming, a metacognitive ROUTER
 * diagnoses what kind of thinking the task needs and composes an ordered sequence of MODE operators
 * (deductive, inductive, abductive, analogical, decompose, causal, bayesian, dialectic, divergent, …),
 * always ending in convergent verification. It returns a record the learning loop (engine/learn.py)
 * uses to get better over time.
 *
 * Usage:  Workflow({ scriptPath: ".../engine/cognitive_engine.js",
 *                    args: { task: "<task>", playbook: {<task_type>: ["mode","ids"]} } })   // playbook optional
 *
 * Mode library mirror of engine/modes.json. Grounding: research/thinking-modes/ + ../METHOD.md.
 */
export const meta = {
  name: 'cognitive-engine',
  description: 'Metacognitive router that picks and sequences thinking-mode operators per problem, executes them, verifies, and emits a learnable record',
  phases: [
    { title: 'Route', detail: 'diagnose what kind of thinking the task needs' },
    { title: 'Think', detail: 'execute the chosen mode sequence' },
    { title: 'Synthesize', detail: 'answer + self-assessment + learning record' },
  ],
}

const A = (typeof args === 'string') ? (args.trim().startsWith('{') ? JSON.parse(args) : { task: args }) : (args || {})
const TASK = A.task || ''
const PLAYBOOK = A.playbook || {}
if (!TASK) throw new Error('cognitive_engine: pass the task via args.task')

const MODES = {
  divergent:        { family: 'divergent',      trigger: 'open-ended design / ideation / novelty is the goal', protocol: 'Name the predictable answer; generate >=5 structurally-different candidates via distinct lenses (analogy, invert, first-principles, blend, extremes); dedupe paraphrases; keep the spread.' },
  decompose:        { family: 'decompositional',trigger: 'complex multi-step / build-implement-plan X / too big for one shot', protocol: 'Break into an ordered list of smaller subproblems (least-to-most); solve each in order feeding earlier answers forward; reassemble.' },
  deductive:        { family: 'deductive',       trigger: 'explicit rules/axioms/constraints / proof / does X follow from Y', protocol: 'List given facts and rules explicitly; apply step by step (forward/backward chaining), each inference a single justified step with no leaps; derive the goal or show it unreachable.' },
  inductive:        { family: 'inductive',       trigger: 'examples given, rule wanted / find the pattern / generalize', protocol: 'Collect examples; hypothesize the SIMPLEST rule fitting them; test against EVERY example, revise on any miss; output rule + support + a counterexample probe.' },
  abductive:        { family: 'abductive',       trigger: 'diagnosis / debugging / root-cause / why did X happen', protocol: 'Enumerate >=3 candidate explanations; for each predict what we WOULD observe; compare to actual evidence; pick best-fit; state what would disconfirm it.' },
  analogical:       { family: 'analogical',      trigger: 'stuck / novel / how does another field solve this', protocol: 'Find a structurally-similar SOLVED problem in another domain; map the correspondence; transfer the solution; mark where the analogy breaks.' },
  first_principles: { family: 'first_principles',trigger: 'challenge the obvious / suspect a false assumption', protocol: 'Strip to fundamental truths/constraints; question every inherited assumption; rebuild from fundamentals ignoring convention.' },
  causal:           { family: 'causal',          trigger: 'cause/effect / intervention / what happens if we change X / counterfactual', protocol: 'Build a small causal model (what affects what); separate correlation from causation; reason about the intervention (do-X) and the counterfactual.' },
  bayesian:         { family: 'probabilistic',   trigger: 'uncertainty / estimation / incomplete info / how likely / risk', protocol: 'State a prior; enumerate hypotheses; weigh each evidence item; update to a posterior; report CALIBRATED confidence and the evidence that would most change it.' },
  dialectic:        { family: 'dialectical',     trigger: 'trade-off / contested decision / should we A or B', protocol: 'Steelman the thesis; steelman the antithesis; find the SYNTHESIS that resolves the tension, or the precise condition that decides it.' },
  convergent_verify:{ family: 'convergent',      trigger: 'finalize / check correctness / before shipping', protocol: 'Re-derive independently (self-consistency); switch hats and try to REFUTE (correctness, edge cases, feasibility); if executable, run it; keep only what survives; report residual risk.' },
  metacognitive:    { family: 'metacognitive',   trigger: 'high uncertainty / do I even know this', protocol: 'State what is known, unknown, assumed; rate confidence; decide if more info or another mode is needed before answering.' },
}
const MENU = Object.entries(MODES).map(([id, m]) => `- ${id} (${m.family}): ${m.trigger}`).join('\n')

const ROUTE_SCHEMA = {
  type: 'object',
  properties: {
    diagnosis: { type: 'string', description: 'what kind of problem this is and what thinking it needs' },
    task_type: { type: 'string', description: 'a short reusable tag, e.g. debug, design, estimate, prove, plan, explain, decide' },
    plan: { type: 'array', items: { type: 'string' }, description: 'ordered list of mode ids to run' },
    rationale: { type: 'string' },
  },
  required: ['diagnosis', 'task_type', 'plan', 'rationale'],
}
const MODE_SCHEMA = {
  type: 'object',
  properties: { mode: { type: 'string' }, output: { type: 'string' }, key_result: { type: 'string', description: 'the one load-bearing takeaway to feed forward' } },
  required: ['mode', 'output', 'key_result'],
}
const SYNTH_SCHEMA = {
  type: 'object',
  properties: {
    answer: { type: 'string' },
    load_bearing_modes: { type: 'array', items: { type: 'string' } },
    self_score: { type: 'number', description: '0..1 calibrated confidence the answer is correct AND non-obvious' },
    why: { type: 'string' },
  },
  required: ['answer', 'load_bearing_modes', 'self_score', 'why'],
}

// ---- Stage 1: route ----
phase('Route')
const prior = PLAYBOOK && Object.keys(PLAYBOOK).length
  ? `\n\nLEARNED PRIORS (mode sequences that worked before, by task_type): ${JSON.stringify(PLAYBOOK)}\nUse them as a hint if this task matches, but override if a different sequence clearly fits better.` : ''
const route = await agent(
  `You are the metacognitive router of a cognitive engine. Diagnose what KIND of thinking this task needs and choose a MINIMAL ordered sequence of modes (1-4) that fits — do NOT default to brainstorming. End the sequence with convergent_verify. Pick only modes whose trigger genuinely matches.\n\nTASK: ${TASK}\n\nMODE MENU:\n${MENU}${prior}`,
  { label: 'route', phase: 'Route', schema: ROUTE_SCHEMA })

let plan = (route.plan || []).filter(id => MODES[id])
if (!plan.length) plan = ['metacognitive']
if (plan[plan.length - 1] !== 'convergent_verify') plan.push('convergent_verify')
log(`Diagnosed "${route.task_type}" -> plan: ${plan.join(' -> ')}`)

// ---- Stage 2: think (sequential; each mode builds on the prior trace) ----
phase('Think')
const trace = []
for (let i = 0; i < plan.length; i++) {
  const id = plan[i]
  const prev = trace.length
    ? `\n\nWORK SO FAR (from earlier modes):\n${trace.map(t => `[${t.mode}] ${t.key_result}`).join('\n')}` : ''
  const r = await agent(
    `Apply ONE thinking mode to the task. Follow its protocol precisely; do not drift into generic brainstorming.\n\nTASK: ${TASK}\nMODE: ${id} (${MODES[id].family})\nPROTOCOL: ${MODES[id].protocol}${prev}`,
    { label: `mode:${id}`, phase: 'Think', schema: MODE_SCHEMA })
  if (r) trace.push({ mode: id, output: r.output, key_result: r.key_result })
}

// ---- Stage 3: synthesize + learning record ----
phase('Synthesize')
const synth = await agent(
  `Synthesize the final answer from the reasoning trace. Be decisive; surface the non-obvious insight; state honest residual risk.\n\nTASK: ${TASK}\nTASK TYPE: ${route.task_type}\nPLAN: ${plan.join(' -> ')}\nTRACE:\n${trace.map(t => `### ${t.mode}\n${t.output}`).join('\n\n').slice(0, 14000)}`,
  { label: 'synthesize', phase: 'Synthesize', schema: SYNTH_SCHEMA })

return {
  task: TASK,
  task_type: route.task_type,
  diagnosis: route.diagnosis,
  plan,
  trace: trace.map(t => ({ mode: t.mode, key_result: t.key_result })),
  answer: synth.answer,
  self_score: synth.self_score,
  why: synth.why,
  load_bearing_modes: synth.load_bearing_modes,
  record: { task_type: route.task_type, plan, self_score: synth.self_score },  // -> engine/learn.py
}
