/*
 * divergence_engine.js — the fan-out Divergence Engine (run with the Workflow tool).
 *
 * The turbocharged form of skill/divergence/SKILL.md: instead of one model running the six stages in
 * its own head, this spawns REAL parallel subagents — one per lens (true population-based divergence)
 * and several refuters per survivor (adversarial verification) — then frontier-selects the winner.
 *
 * Usage:  Workflow({ scriptPath: ".../harness/divergence_engine.js", args: "<your task / question>" })
 *         (or args: { task: "...", lenses: 6, survivors: 3, refuters: 3 })
 *
 * Grounding for every stage is in ../METHOD.md. Self-contained: the novelty gate is a tiny lexical
 * port of ../src/novelty.py (workflow scripts can't shell out to Python).
 */

export const meta = {
  name: 'divergence-engine',
  description: 'Population-based divergence: lens agents generate, a novelty archive dedupes, survivors recombine, deepen, get adversarially refuted, and the novelty×value winner is selected',
  phases: [
    { title: 'Frame', detail: 'name the predictable mode to beat' },
    { title: 'Diverge', detail: 'one subagent per lens, mining the low-probability tail' },
    { title: 'Recombine', detail: 'breed the most distant survivors' },
    { title: 'Deepen+Verify', detail: 'expand each survivor, then adversarially refute it' },
    { title: 'Select', detail: 'frontier-select novel AND correct' },
  ],
}

// ---- inputs ----
// Accept args as: a plain task string, an {task,lenses,...} object, OR a JSON string of that object
// (the Workflow tool may hand the args through as a string).
let A = args
if (typeof A === 'string') {
  const s = A.trim()
  if (s.startsWith('{')) { try { A = JSON.parse(s) } catch { A = { task: A } } }
  else A = { task: A }
}
A = A || {}
const TASK = A.task || ''
const N_LENSES = A.lenses || 6
const N_SURVIVORS = A.survivors || 3
const N_REFUTERS = A.refuters || 3
if (!TASK) throw new Error('divergence_engine: pass the task via args (string) or args.task')

// ---- lexical novelty gate (port of src/novelty.py) ----
function ngrams(s, n = 4) {
  s = (s || '').toLowerCase().replace(/\s+/g, ' ').trim()
  const set = new Set()
  if (s.length < n) { if (s) set.add(s); return set }
  for (let i = 0; i <= s.length - n; i++) set.add(s.slice(i, i + n))
  return set
}
function dist(a, b) {
  const A = ngrams(a), B = ngrams(b)
  if (!A.size && !B.size) return 0
  let inter = 0; for (const x of A) if (B.has(x)) inter++
  const uni = A.size + B.size - inter
  return 1 - (uni ? inter / uni : 0)
}
function setDiversity(arr) {
  if (arr.length < 2) return 0
  let s = 0, c = 0
  for (let i = 0; i < arr.length; i++) for (let j = i + 1; j < arr.length; j++) { s += dist(arr[i], arr[j]); c++ }
  return s / c
}
function selectDiverse(arr, k) {
  if (k >= arr.length) return arr.map((_, i) => i)
  let seed = 0, best = -1
  for (let i = 0; i < arr.length; i++) {
    let m = 0; for (let j = 0; j < arr.length; j++) if (i !== j) m += dist(arr[i], arr[j])
    m /= (arr.length - 1); if (m > best) { best = m; seed = i }
  }
  const chosen = [seed]
  while (chosen.length < k) {
    let nxt = -1, bb = -1
    for (let i = 0; i < arr.length; i++) {
      if (chosen.includes(i)) continue
      let mn = Infinity; for (const c of chosen) mn = Math.min(mn, dist(arr[i], arr[c]))
      if (mn > bb) { bb = mn; nxt = i }
    }
    chosen.push(nxt)
  }
  return chosen
}
const text = (c) => `${c.lens || ''} ${c.summary || ''} ${c.approach || ''}`

const LENSES = [
  { key: 'analogy', instr: 'Solve it the way a COMPLETELY DIFFERENT domain solves its version of this problem (biology, logistics, games, finance, distributed systems, ecology). Name the domain and the transfer.' },
  { key: 'step-back', instr: 'Abstract to the most general principle underneath the task, then re-specialize it in a way the obvious solution does NOT.' },
  { key: 'invert', instr: 'Find the thing everyone treats as fixed/given here, and make IT the variable. Invert the core constraint.' },
  { key: 'first-principles', instr: 'Rederive a solution from scratch, deliberately ignoring how this is "normally" done. Question whether the task even needs to exist.' },
  { key: 'blend', instr: 'Fuse two unrelated existing solutions/tools into one hybrid that neither alone provides.' },
  { key: 'extremes', instr: 'Apply SCAMPER extremes: remove the part everyone considers essential, OR push one dimension to 100x. See what becomes possible.' },
].slice(0, N_LENSES)

const CAND_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' }, summary: { type: 'string' }, approach: { type: 'string' },
    conventionality_p: { type: 'number', description: '0 = nobody does this, 1 = the obvious default' },
  },
  required: ['lens', 'summary', 'approach', 'conventionality_p'],
}
const DEEP_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' }, plan: { type: 'string', description: 'how it actually plays out, where it forks, dead-ends backtracked' },
    key_risk: { type: 'string' },
  }, required: ['summary', 'plan', 'key_risk'],
}
const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    survives: { type: 'boolean' }, strongest_objection: { type: 'string' },
    feasibility: { type: 'number', description: '0..1' },
  }, required: ['survives', 'strongest_objection', 'feasibility'],
}
const SELECT_SCHEMA = {
  type: 'object',
  properties: {
    winner_summary: { type: 'string' }, winner_plan: { type: 'string' },
    why_beats_mode: { type: 'string' }, honest_risk: { type: 'string' }, runner_up: { type: 'string' },
  }, required: ['winner_summary', 'winner_plan', 'why_beats_mode', 'honest_risk'],
}

// ---- Stage 0: name the mode ----
phase('Frame')
const mode = await agent(
  `For this task, state in 1-2 sentences the SINGLE most predictable answer — what a competent but unimaginative agent would output. This is the baseline we must beat; do not solve the task.\n\nTASK: ${TASK}`,
  { label: 'name-the-mode', phase: 'Frame' })

// ---- Stage 1: diverge (one subagent per lens, in parallel) ----
phase('Diverge')
const raw = (await parallel(LENSES.map(L => () =>
  agent(
    `You are one lens in a divergence engine. Produce ONE genuinely non-obvious approach to the task using your assigned lens. Mine the low-probability tail; avoid the predictable mode.\n\nTASK: ${TASK}\nTHE MODE TO AVOID: ${mode}\nYOUR LENS (${L.key}): ${L.instr}\n\nReturn a candidate with an honest conventionality_p (be ruthless — if it's a common answer, say so).`,
    { label: `lens:${L.key}`, phase: 'Diverge', schema: CAND_SCHEMA }
  )))).filter(Boolean)

// ---- Stage 2: novelty gate ----
const div1 = setDiversity(raw.map(text))
log(`Diverge: ${raw.length} candidates, set_diversity=${div1.toFixed(3)}`)
let pool = raw.slice()
// keep the most diverse spread (and prefer low-conventionality on ties via a light penalty in ordering)
const keepN = Math.min(pool.length, Math.max(N_SURVIVORS + 1, 4))
const keepIdx = selectDiverse(pool.map(text), keepN)
pool = keepIdx.map(i => pool[i])

// ---- Stage 3: recombine the two most distant survivors ----
phase('Recombine')
const di = selectDiverse(pool.map(text), Math.min(2, pool.length))
if (di.length === 2) {
  const hybrid = await agent(
    `Breed these two approaches into a HYBRID that neither alone provides. Keep what is strong in each; resolve their tension.\n\nTASK: ${TASK}\nA: ${JSON.stringify(pool[di[0]])}\nB: ${JSON.stringify(pool[di[1]])}`,
    { label: 'recombine', phase: 'Recombine', schema: CAND_SCHEMA })
  if (hybrid) pool.push(hybrid)
}
// final survivor set: most-diverse N_SURVIVORS
const survIdx = selectDiverse(pool.map(text), Math.min(N_SURVIVORS, pool.length))
const survivors = survIdx.map(i => pool[i])
log(`Survivors: ${survivors.length} (final set_diversity=${setDiversity(survivors.map(text)).toFixed(3)})`)

// ---- Stage 4+5: deepen each survivor, then adversarially verify (pipelined per survivor) ----
phase('Deepen+Verify')
const verified = await pipeline(
  survivors,
  (c) => agent(
    `Expand this approach into a concrete plan: how it actually plays out, where it forks, which dead-ends you backtrack from. Be specific.\n\nTASK: ${TASK}\nAPPROACH: ${JSON.stringify(c)}`,
    { label: `deepen:${c.lens}`, phase: 'Deepen+Verify', schema: DEEP_SCHEMA }),
  (deep, c) => parallel(Array.from({ length: N_REFUTERS }, (_, r) => () =>
    agent(
      `You are an adversarial refuter (#${r + 1}). Try HARD to break this approach: correctness, feasibility, hidden cost, why it fails in practice. If it is executable, reason about what running it would reveal. Default to survives=false if genuinely uncertain.\n\nTASK: ${TASK}\nAPPROACH: ${JSON.stringify(deep)}`,
      { label: `refute:${c.lens}#${r + 1}`, phase: 'Deepen+Verify', schema: VERDICT_SCHEMA })
  )).then(vs => {
    const v = vs.filter(Boolean)
    const survives = v.filter(x => x.survives).length > v.length / 2
    const feas = v.length ? v.reduce((s, x) => s + (x.feasibility || 0), 0) / v.length : 0
    return { candidate: c, deep, survives, feasibility: feas, objections: v.map(x => x.strongest_objection) }
  })
).then(rs => rs.filter(Boolean))

const cleared = verified.filter(v => v.survives)
log(`Verified: ${cleared.length}/${verified.length} survivors cleared adversarial refutation`)

// ---- Stage 6: frontier select (novel AND correct) ----
phase('Select')
const pickPool = (cleared.length ? cleared : verified)
const selection = await agent(
  `Frontier-select the final answer. Choose the MOST NOVEL approach among those that clear the quality bar — rare-and-good beats common-and-good. Do NOT default to the safest. Synthesize the winner (you may graft the best idea from a runner-up). Explain why it beats the mode.\n\nTASK: ${TASK}\nTHE MODE (baseline to beat): ${mode}\nCANDIDATES (with verification + feasibility):\n${JSON.stringify(pickPool.map(v => ({ lens: v.candidate.lens, conventionality_p: v.candidate.conventionality_p, plan: v.deep, survives: v.survives, feasibility: v.feasibility, objections: v.objections })), null, 1).slice(0, 14000)}`,
  { label: 'frontier-select', phase: 'Select', schema: SELECT_SCHEMA })

return {
  task: TASK,
  mode_baseline: mode,
  diversity: { initial: div1, survivors: setDiversity(survivors.map(text)) },
  candidates_considered: raw.length,
  survivors_cleared: cleared.length,
  selection,
}
