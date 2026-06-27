"""
learn.py — the self-improvement loop for the Cognitive Engine.

The engine emits a record {task_type, plan, self_score} per run. This accumulates a persistent PLAYBOOK
mapping task_type -> which mode-plan scored best, so the router can bias future routing toward what has
worked (exploitation) while still exploring. That is the mechanism by which the engine "keeps becoming
better": its routing priors are learned, not fixed.

HONEST SCOPE: by default the score is the engine's SELF-assessed confidence, which is a weak signal
(a model grading itself). The loop is score-source-agnostic: pass an EXTERNAL score (a benchmark
checker's pass/fail, a novelty metric, a human rating) via `score` and the playbook improves on a real
signal. We label which source produced each record so self-scored and externally-scored evidence are
never silently mixed.

Usage:
  python engine/learn.py record '{"task_type":"debug","plan":["abductive","convergent_verify"],"self_score":0.8}' [--source self|external]
  python engine/learn.py recommend debug
  python engine/learn.py show
ponytail: stdlib only.
"""
import json, os, sys

PB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "playbook.json")


def load():
    if os.path.exists(PB):
        return json.load(open(PB, encoding="utf-8"))
    return {"_doc": "Learned routing priors: task_type -> plan -> running stats. Updated by engine/learn.py.", "by_type": {}}


def save(pb):
    json.dump(pb, open(PB, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def record(task_type, plan, score, source="self"):
    pb = load()
    bt = pb["by_type"].setdefault(task_type, {})
    key = ">".join(plan)
    e = bt.setdefault(key, {"uses": 0, "sum": 0.0, "avg": 0.0, "sources": {}})
    e["uses"] += 1
    e["sum"] += float(score)
    e["avg"] = e["sum"] / e["uses"]
    e["sources"][source] = e["sources"].get(source, 0) + 1
    save(pb)
    return e


def recommend(task_type, min_uses=2, prefer_external=True):
    """Best-known plan for a task_type. Prefers plans with external evidence; needs min_uses to trust."""
    pb = load()
    bt = pb["by_type"].get(task_type, {})
    if not bt:
        return None
    def quality(e):
        ext = e["sources"].get("external", 0)
        seen = e["uses"]
        # rank by avg, gated on enough uses; bonus for external evidence
        trusted = seen >= min_uses
        return (1 if (trusted and (not prefer_external or ext > 0)) else 0, e["avg"], seen)
    best = max(bt.items(), key=lambda kv: quality(kv[1]))
    return {"plan": best[0].split(">"), **best[1]}


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "record":
        rec = json.loads(sys.argv[2])
        src = "self"
        if "--source" in sys.argv:
            src = sys.argv[sys.argv.index("--source") + 1]
        score = rec.get("self_score", rec.get("score", 0.0))
        e = record(rec["task_type"], rec["plan"], score, src)
        print(f"recorded {rec['task_type']} :: {'>'.join(rec['plan'])} -> avg={e['avg']:.3f} uses={e['uses']}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "recommend":
        print(json.dumps(recommend(sys.argv[2]), indent=2))
    elif len(sys.argv) >= 2 and sys.argv[1] == "show":
        print(json.dumps(load(), indent=2, ensure_ascii=False))
    else:
        # self-check: external evidence beats a higher self-score with no external backing
        import tempfile
        PB = os.path.join(tempfile.gettempdir(), "_pb_test.json")
        if os.path.exists(PB): os.unlink(PB)
        record("debug", ["abductive", "convergent_verify"], 0.7, "external")
        record("debug", ["abductive", "convergent_verify"], 0.9, "external")
        record("debug", ["divergent", "convergent_verify"], 0.95, "self")
        record("debug", ["divergent", "convergent_verify"], 0.95, "self")
        rec = recommend("debug")
        assert rec["plan"] == ["abductive", "convergent_verify"], rec
        print("learn.py self-check passed: externally-validated plan preferred over higher self-scored one")
        os.unlink(PB)
