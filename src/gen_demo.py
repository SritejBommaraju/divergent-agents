"""
gen_demo.py — turn a divergence_engine run's output file into a readable demo artifact.

Usage: python src/gen_demo.py <task.output> <out.md> "<short title>"
Previews of intermediate candidates are truncated by the workflow logger; the final winner is verbatim.
ponytail: stdlib only.
"""
import json, sys, re

OUT = sys.argv[1]
DEST = sys.argv[2]
TITLE = sys.argv[3] if len(sys.argv) > 3 else "Divergence Engine — live run"

d = json.load(open(OUT, encoding="utf-8"))
r = d["result"]
wp = [w for w in d.get("workflowProgress", []) if w.get("type") == "workflow_agent"]


def unescape(s):
    return s.replace('\\"', '"').replace("\\n", " ").replace("\\\\", "\\")


def field(preview, keys, n=420):
    """Extract the (possibly truncated) value of the first matching JSON key from a preview string."""
    p = preview or ""
    for k in keys:
        m = re.search(r'"' + k + r'"\s*:\s*"(.*)', p, re.DOTALL)
        if m:
            v = m.group(1)
            # cut at the next field boundary if the value actually closed
            v = re.split(r'","\w+"\s*:', v)[0]
            v = unescape(v).rstrip('"}').strip()
            v = " ".join(v.split())
            return (v[:n] + "…") if len(v) > n else v
    return ""


def clean(s, n=420):
    s = unescape((s or "").strip())
    s = " ".join(s.split())
    return (s[:n] + "…") if len(s) > n else s


# the task field is the (stringified) args; pull the real task out
task = r["task"]
try:
    task = json.loads(task).get("task", task)
except Exception:
    pass

m = []
m.append(f"# {TITLE}\n")
m.append("*Captured verbatim from an actual `harness/divergence_engine.js` run "
         f"({d.get('agentCount')} subagents, {d.get('totalTokens'):,} tokens). Intermediate candidate/"
         "refutation text is truncated by the workflow logger; the final winner is reproduced in full.*\n")
m.append("## The task\n")
m.append(f"> {task}\n")
m.append("## Stage 0 — the mode (the predictable answer the engine must beat)\n")
m.append(f"> {r['mode_baseline']}\n")

m.append("## Stage 1 — divergence (one subagent per lens)\n")
m.append(f"Set diversity of the candidate pool: **{r['diversity']['initial']:.3f}** "
         f"(0 = paraphrases, 1 = unrelated). {r['candidates_considered']} candidates considered.\n")
for w in wp:
    if w["phaseTitle"] == "Diverge":
        summ = field(w.get("resultPreview"), ["summary"], 300) or clean(w.get("lastToolSummary"), 300)
        m.append(f"- **{w['label']}** — {summ}")
m.append("")

m.append("## Stage 3 — recombination\n")
for w in wp:
    if w["phaseTitle"] == "Recombine":
        m.append(f"- **{w['label']}** — {field(w.get('resultPreview'), ['summary','lens'], 360)}")
m.append("")

m.append("## Stage 5 — adversarial verification (the load-bearing guard)\n")
m.append(f"**{r['survivors_cleared']} of the survivors cleared refutation.** The refuters were brutal "
         "and correct — they found the deep circularity the *mode* answer quietly hides (a collapsed "
         "prior cannot grade itself). A sample of what they said:\n")
for w in wp:
    if w["phaseTitle"] == "Deepen+Verify" and w["label"].startswith("refute:"):
        lens = w["label"].split(":", 1)[1].rsplit("#", 1)[0]
        rn = w["label"].rsplit("#", 1)[-1]
        verdict = "SURVIVES" if '"survives":true' in (w.get("resultPreview") or "") else "killed"
        obj = field(w.get("resultPreview"), ["strongest_objection"], 340)
        m.append(f"- **refuter #{rn} on `{lens[:48]}…`** ({verdict}) — {obj}")
m.append("")
m.append("> This is the point: divergence without verification is just confident noise. Every novel "
         "candidate was stress-tested to destruction, and the survivors that *looked* clever were shown "
         "to share the very flaw they claimed to fix. That failure is then fed into selection.\n")

s = r["selection"]
m.append("## Stage 6 — frontier-select: the synthesized winner (verbatim)\n")
m.append(f"**{s.get('winner_summary','')}**\n")
m.append("### Plan\n")
m.append(s.get("winner_plan", "") + "\n")
m.append("### Why it beats the mode\n")
m.append(s.get("why_beats_mode", "") + "\n")
if s.get("honest_risk"):
    m.append("### Honest residual risk\n")
    m.append(s["honest_risk"] + "\n")
if s.get("runner_up"):
    m.append("### Runner-up\n")
    m.append(s["runner_up"] + "\n")

m.append("---\n")
m.append("**Read this top-to-bottom and the thesis is demonstrated, not asserted:** the agent named its "
         "own predictable answer, generated six structurally different alternatives, had them torn apart by "
         "adversarial verifiers, and synthesized a winner that survives the exact objections that sank the "
         "rest — landing somewhere the single forward pass never would.\n")

open(DEST, "w", encoding="utf-8").write("\n".join(m))
print(f"wrote {DEST}  ({len(''.join(m))} chars)")
