"""
recheck_arxiv.py — independent ground-truth re-verification of every arXiv id we cite.

Hits the official arXiv API directly (polite UA, chunked, backoff on 429), parses the Atom feed
ourselves, and reports which ids resolved vs not. This is a second, independent pass on top of the
workflow's verifier agents. ponytail: stdlib only (urllib, xml, time, json).
"""
import json, os, time, urllib.request, urllib.error, xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS = os.path.join(REPO, "research", "papers.json")
ATOM = "{http://www.w3.org/2005/Atom}"
UA = "divergent-agents-research/1.0 (mailto:sritejbommaraju@berkeley.edu)"


def fetch(ids):
    url = "http://export.arxiv.org/api/query?max_results=100&id_list=" + ",".join(ids)
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 5 * (attempt + 1)
                print(f"  429 — backing off {wait}s (attempt {attempt+1})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("exhausted retries")


def parse(feed):
    root = ET.fromstring(feed)
    out = {}
    for e in root.findall(f"{ATOM}entry"):
        idtext = (e.findtext(f"{ATOM}id") or "")
        title = " ".join((e.findtext(f"{ATOM}title") or "").split())
        # an arxiv "id" url like http://arxiv.org/abs/2305.10601v3
        aid = idtext.rsplit("/", 1)[-1]
        base = aid.split("v")[0]
        # arXiv returns an error entry (no abs/) when an id is bad
        if "/abs/" in idtext:
            out[base] = title
    return out


def main():
    papers = json.load(open(PAPERS, encoding="utf-8"))
    ids = sorted({(p.get("arxiv_id") or "").strip() for p in papers if (p.get("arxiv_id") or "").strip()})
    print(f"Re-checking {len(ids)} arXiv ids against export.arxiv.org\n")
    resolved = {}
    CHUNK = 15
    chunks = [ids[i:i + CHUNK] for i in range(0, len(ids), CHUNK)]
    for i, ch in enumerate(chunks):
        print(f"chunk {i+1}/{len(chunks)} ({len(ch)} ids)")
        resolved.update(parse(fetch(ch)))
        if i < len(chunks) - 1:
            time.sleep(4)  # arXiv asks ~3s between calls
    missing = [i for i in ids if i not in resolved]
    print(f"\nRESOLVED: {len(resolved)}/{len(ids)}")
    if missing:
        print("MISSING (did NOT resolve):", missing)
    else:
        print("MISSING: none — every cited arXiv id resolves to a real paper.")
    json.dump({"requested": ids, "resolved": resolved, "missing": missing},
              open(os.path.join(REPO, "research", "arxiv_recheck.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("\nSample resolved id | title:")
    for i in ids[:6]:
        print(f"  {i} | {resolved.get(i,'<MISSING>')}")


if __name__ == "__main__":
    main()
