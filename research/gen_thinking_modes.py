"""
gen_thinking_modes.py — turn the thinking-modes research run into repo artifacts.

Writes research/thinking-modes/{REPORT.md, papers.json, modes.json} and prints arXiv ids for an
independent re-verification. ponytail: stdlib only.
"""
import json, os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else (
    "C:/Users/bomma/AppData/Local/Temp/claude/"
    "C--Users-bomma-Desktop-innovator/c3cd8775-0d0d-45f8-8c6e-cde01d170454/tasks/wrpk1s67w.output")
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "thinking-modes")
os.makedirs(DEST, exist_ok=True)
d = json.load(open(OUT, encoding="utf-8"))
themes = d["result"]["themes"]

papers, modes = [], []
for th in themes:
    for p in th.get("verified_papers", []):
        papers.append({**p, "theme_key": th["key"]})
    for m in th.get("modes", []):
        modes.append({**m, "theme_key": th["key"]})
json.dump(papers, open(os.path.join(DEST, "papers.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump(modes, open(os.path.join(DEST, "modes.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def link(p):
    return f"[{p.get('title','?')}]({p.get('url','')})" if p.get("url") else p.get("title", "?")

m = ["# Thinking modes — the grounded cognitive library\n",
     "*Verified evidence base for the Cognitive Engine (`engine/`). Each mode operator below is grounded "
     f"in a real, re-checked paper. {sum(1 for p in papers if p.get('exists'))}/{len(papers)} papers confirmed real.*\n"]
for th in themes:
    m.append(f"\n## {th['title']}\n")
    if th.get("routing_signals"):
        m.append("**Routing signals — when this family of thinking is needed**\n")
        m += [f"- {s}" for s in th["routing_signals"]] + [""]
    if th.get("modes"):
        m.append("**Mode operators**\n")
        for mo in th["modes"]:
            m.append(f"- **{mo.get('name','?')}** *({mo.get('family','?')})* — trigger: {mo.get('trigger','—')}")
            m.append(f"  - protocol: {mo.get('protocol','—')}")
            m.append(f"  - grounding: {mo.get('grounding','—')}")
        m.append("")
    m.append("**Papers**\n")
    for p in th.get("verified_papers", []):
        aid = (p.get("arxiv_id") or "").strip()
        tag = f"arXiv:{aid}" if aid and "N/A" not in aid else (p.get("venue") or "—")
        flag = "✅" if p.get("exists") else "❌"
        m.append(f"- {flag} {link(p)} — *{p.get('authors','—')}* ({p.get('year','—')}, {tag})  ")
        m.append(f"  **Finding.** {p.get('finding','—')}  ")
        m.append(f"  **Grounds.** {p.get('mode_relevance','—')}  ")
        m.append(f"  *Verified via {p.get('verification_method','—')}.*")
    m.append("")
open(os.path.join(DEST, "REPORT.md"), "w", encoding="utf-8").write("\n".join(m))

real = [p for p in papers if p.get("exists")]
ids = sorted({(p.get("arxiv_id") or "").strip() for p in real
              if (p.get("arxiv_id") or "").strip() and "N/A" not in (p.get("arxiv_id") or "")})
print(f"themes={len(themes)} papers={len(papers)} real={len(real)} modes={len(modes)}")
print("ARXIV_IDS:", ",".join(ids))
