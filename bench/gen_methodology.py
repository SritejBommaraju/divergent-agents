"""
gen_methodology.py — turn the benchmarking-methodology research run into repo artifacts.

Emits:
  bench/methodology_papers.json   machine-readable list of every methodology paper
  bench/methodology_papers.md     linked appendix: per-theme protocol + honesty traps + papers
Prints the arXiv ids for an independent batch re-verification. ponytail: stdlib only.
"""
import json, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else (
    "C:/Users/bomma/AppData/Local/Temp/claude/"
    "C--Users-bomma-Desktop-innovator/c3cd8775-0d0d-45f8-8c6e-cde01d170454/tasks/wuqgle7sc.output")
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(OUT, encoding="utf-8"))
themes = d["result"]["themes"]

papers = []
for th in themes:
    for p in th.get("verified_papers", []):
        p = dict(p); p["theme_key"] = th["key"]; papers.append(p)
json.dump(papers, open(os.path.join(HERE, "methodology_papers.json"), "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)


def link(p):
    t = p.get("title", "?").replace("|", "\\|")
    return f"[{t}]({p.get('url','')})" if p.get("url") else t


m = ["# Benchmarking methodology — papers, protocols & honesty traps\n",
     "*The verified evidence base behind [`../BENCHMARKING.md`](../BENCHMARKING.md). "
     f"{sum(len(t.get('verified_papers',[])) for t in themes)} papers, "
     f"{sum(1 for p in papers if p.get('exists'))} confirmed real. "
     "Re-verification ledger appended by `bench/recheck_methodology.py`.*\n"]
for th in themes:
    m.append(f"\n## {th['title']}\n")
    if th.get("recommended_protocol"):
        m.append("**Recommended protocol**\n")
        m += [f"{i+1}. {s}" for i, s in enumerate(th["recommended_protocol"])] + [""]
    if th.get("honesty_traps"):
        m.append("**Honesty traps (how this measurement can lie) & fixes**\n")
        m += [f"- {s}" for s in th["honesty_traps"]] + [""]
    m.append("**Papers**\n")
    for p in th.get("verified_papers", []):
        aid = (p.get("arxiv_id") or "").strip()
        tag = f"arXiv:{aid}" if aid and "N/A" not in aid else (p.get("venue") or "—")
        flag = "✅" if p.get("exists") else "❌"
        m.append(f"- {flag} {link(p)} — *{p.get('authors','—')}* ({p.get('year','—')}, {tag})  ")
        m.append(f"  **Finding.** {p.get('finding','—')}  ")
        m.append(f"  **Use.** {p.get('how_to_use','—')}  ")
        m.append(f"  *Verified via {p.get('verification_method','—')}.*")
    m.append("")
open(os.path.join(HERE, "methodology_papers.md"), "w", encoding="utf-8").write("\n".join(m))

real = [p for p in papers if p.get("exists")]
ids = sorted({(p.get("arxiv_id") or "").strip() for p in real
              if (p.get("arxiv_id") or "").strip() and "N/A" not in (p.get("arxiv_id") or "")})
print(f"themes={len(themes)} papers={len(papers)} real={len(real)}")
print("ARXIV_IDS:", ",".join(ids))
print("NON-ARXIV REAL:")
for p in real:
    if not ((p.get("arxiv_id") or "").strip()) or "N/A" in (p.get("arxiv_id") or ""):
        print(f"  - {p['title']}  | {p.get('url')}")
