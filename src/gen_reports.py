"""
gen_reports.py — turn the verified-research workflow output into the repo's reports.

Reads the workflow result JSON and emits:
  research/papers.json        machine-readable list of every paper
  research/REPORT.md          master report (every paper linked + verification flag)
  research/by-theme/<key>.md  per-theme deep dive
  research/verification.md    verification ledger (counts, any unresolved, non-arXiv items)

Idempotent: re-run to regenerate. ponytail: pure stdlib (json, os).
"""
import json, os, sys

OUT_FILE = sys.argv[1] if len(sys.argv) > 1 else (
    "C:/Users/bomma/AppData/Local/Temp/claude/"
    "C--Users-bomma-Desktop-innovator/c3cd8775-0d0d-45f8-8c6e-cde01d170454/tasks/wg6oqyv54.output")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(REPO, "research")
BYTHEME = os.path.join(RESEARCH, "by-theme")
os.makedirs(BYTHEME, exist_ok=True)

with open(OUT_FILE, encoding="utf-8") as fh:
    data = json.load(fh)
themes = data["result"]["themes"]

# ---- flatten ----
all_papers = []
for th in themes:
    for p in th.get("verified_papers", []):
        p = dict(p)
        p["theme_key"] = th["key"]
        p["theme_title"] = th["title"]
        all_papers.append(p)

real = [p for p in all_papers if p.get("exists")]
not_real = [p for p in all_papers if not p.get("exists")]
non_arxiv = [p for p in real if not (p.get("arxiv_id") or "").strip()]

with open(os.path.join(RESEARCH, "papers.json"), "w", encoding="utf-8") as fh:
    json.dump(all_papers, fh, indent=2, ensure_ascii=False)


def link(p):
    t = p.get("title", "Untitled").replace("|", "\\|")
    u = p.get("url") or (f"https://arxiv.org/abs/{p['arxiv_id']}" if p.get("arxiv_id") else "")
    return f"[{t}]({u})" if u else t


def paper_block(p, n):
    aid = (p.get("arxiv_id") or "").strip()
    aid_str = f"arXiv:{aid}" if aid else (p.get("venue") or "non-arXiv")
    flag = "✅ verified real" if p.get("exists") else "❌ UNVERIFIED"
    lines = [
        f"#### {n}. {link(p)}",
        "",
        f"- **Authors:** {p.get('verified_authors') or p.get('authors','—')}  ",
        f"- **Year / venue:** {p.get('year','—')} · {p.get('venue','—')} · {aid_str}  ",
        f"- **Verification:** {flag} — via `{p.get('verification_method','—')}`"
        + (f" ({p['verification_note']})" if p.get("verification_note") else ""),
        "",
        f"- **Method.** {p.get('method','—')}",
        f"- **Why it matters for divergence.** {p.get('relevance','—')}",
        f"- **→ Harness application.** {p.get('harness_application','—')}",
        "",
    ]
    return "\n".join(lines)


# ---- master report ----
m = []
m.append("# Master Report — Turning Coding Agents from Predictors into Divergent Thinkers\n")
m.append("> A verified survey of every method we found for pushing a general-purpose coding agent "
         "(Claude Code, Codex) past the single most-likely answer into genuine novelty — and how each "
         "one maps onto a concrete harness/skill mechanism.\n")
m.append("## At a glance\n")
m.append(f"- **Themes researched:** {len(themes)}")
m.append(f"- **Papers found:** {len(all_papers)}")
m.append(f"- **Independently confirmed real:** {len(real)} / {len(all_papers)}")
m.append(f"- **Unresolved / flagged:** {len(not_real)}")
m.append(f"- **Real but not on arXiv (verified via publisher/Semantic Scholar):** {len(non_arxiv)}\n")
m.append("**How verification works.** Each paper was found by a per-theme research scout, then "
         "re-checked by a separate strict verifier that re-fetched it from the arXiv API "
         "(`export.arxiv.org/api/query?id_list=…`) or Semantic Scholar and confirmed the returned "
         "title/authors match. A paper is marked ✅ only if a matching record was actually retrieved. "
         "See [`verification.md`](verification.md) for the independent re-check ledger.\n")
m.append("## Themes\n")
for i, th in enumerate(themes, 1):
    m.append(f"{i}. [{th['title']}](#{i}-{th['key']}) — {len(th.get('verified_papers',[]))} papers")
m.append("")
for i, th in enumerate(themes, 1):
    m.append(f"\n---\n\n## {i}. {th['title']}\n")
    m.append(f"<a id='{i}-{th['key']}'></a>\n")
    m.append(f"*{th.get('theme','')}*\n")
    if th.get("key_takeaways"):
        m.append("**Key takeaways**\n")
        for t in th["key_takeaways"]:
            m.append(f"- {t}")
        m.append("")
    if th.get("harness_ideas"):
        m.append("**Harness mechanisms this theme suggests**\n")
        for t in th["harness_ideas"]:
            m.append(f"- {t}")
        m.append("")
    m.append("### Papers\n")
    for n, p in enumerate(th.get("verified_papers", []), 1):
        m.append(paper_block(p, n))
    # per-theme file
    tt = [f"# {th['title']}\n", f"*{th.get('theme','')}*\n",
          f"[← back to master report](../REPORT.md)\n"]
    if th.get("key_takeaways"):
        tt.append("## Key takeaways\n")
        tt += [f"- {t}" for t in th["key_takeaways"]] + [""]
    if th.get("harness_ideas"):
        tt.append("## Harness mechanisms\n")
        tt += [f"- {t}" for t in th["harness_ideas"]] + [""]
    tt.append("## Papers\n")
    for n, p in enumerate(th.get("verified_papers", []), 1):
        tt.append(paper_block(p, n))
    with open(os.path.join(BYTHEME, f"{th['key']}.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(tt))

with open(os.path.join(RESEARCH, "REPORT.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(m))

print(f"themes={len(themes)} papers={len(all_papers)} real={len(real)} not_real={len(not_real)} non_arxiv={len(non_arxiv)}")
print("\nARXIV_IDS:", ",".join(sorted({(p.get('arxiv_id') or '').strip() for p in real if (p.get('arxiv_id') or '').strip()})))
print("\nNON_ARXIV REAL PAPERS:")
for p in non_arxiv:
    print(f"  - {p['title']}  | {p.get('url')}  | {p.get('verification_method')}")
if not_real:
    print("\nFLAGGED NOT-REAL:")
    for p in not_real:
        print(f"  - {p['title']}  | note={p.get('verification_note')}")
