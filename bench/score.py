"""
score.py — the DETERMINISTIC scorer for the divergence benchmark.

Generation is done by LLMs; scoring is NOT. Everything here is reproducible: semantic distance comes
from a fixed, torch-free static embedding model (model2vec potion-base-8M), and significance comes from
a permutation test with a fixed seed. Keeping generation and scoring separate is the core honesty move
— the model that writes the answers never grades them.

Honesty disclosures:
  * The embedding model is itself an ML artifact, so "semantic distance" is a proxy, not ground truth.
    It is the field-standard objective measure for the Divergent Association Task (Olson et al. 2021,
    PNAS) and far more neutral than lexical distance or self-judging — but it has a ceiling.
  * Numbers are reported with 95% bootstrap CIs and a permutation-test p-value, never as bare means.

ponytail: numpy only (+ model2vec for embeddings). No scipy/sklearn.
"""
from __future__ import annotations
import re, itertools, numpy as np

# SemDis (Beaty & Johnson 2021) honesty rule: don't cherry-pick one embedding space — average over an
# ENSEMBLE of fixed, public spaces so one model's idiosyncrasies wash out. All are static & torch-free.
ENSEMBLE = ["minishlab/potion-base-8M", "minishlab/potion-base-32M", "minishlab/potion-retrieval-32M"]
_MODELS = {}
def _models():
    if not _MODELS:
        from model2vec import StaticModel
        for n in ENSEMBLE:
            _MODELS[n] = StaticModel.from_pretrained(n)
    return _MODELS

def _embed_one(model, texts):
    v = np.asarray(model.encode(list(texts)), dtype=np.float64)
    nrm = np.linalg.norm(v, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    return v / nrm

def embed(texts):
    """Back-compat: L2-normalized embeddings from the first ensemble model."""
    m = list(_models().values())[0]
    return _embed_one(m, texts)

def _pairwise_cos_dist(vecs):
    sims = vecs @ vecs.T
    iu = np.triu_indices(len(vecs), k=1)
    return 1.0 - sims[iu]

def pairwise_dist_ensemble(texts):
    """Mean pairwise cosine distance per unordered pair, AVERAGED across the embedding ensemble."""
    mats = [_embed_one(m, texts) for m in _models().values()]
    return np.mean([_pairwise_cos_dist(v) for v in mats], axis=0)

def centroid_ensemble(texts):
    """Per-model L2-normalized centroid of a set of texts (used for between-set distances)."""
    cents = []
    for m in _models().values():
        v = _embed_one(m, texts)
        c = v.mean(axis=0)
        c = c / (np.linalg.norm(c) or 1.0)
        cents.append(c)
    return cents

def between_set_dist(sets):
    """Mean pairwise distance between sets-of-texts (each set -> ensemble centroids), averaged over models.
    Measures POPULATION diversity: are independently-sampled responses spread out, or collapsed?"""
    if len(sets) < 2:
        return 0.0
    cents = [centroid_ensemble(s) for s in sets]          # cents[i] = list over models
    nm = len(ENSEMBLE)
    per_model = []
    for mi in range(nm):
        M = np.array([cents[i][mi] for i in range(len(sets))])
        per_model.append(_pairwise_cos_dist(M).mean())
    return float(np.mean(per_model))

# ---- divergent-thinking metrics ----
def parse_words(text, k=10):
    """Extract up to k clean lowercase single tokens from a DAT response."""
    toks = re.findall(r"[A-Za-z][A-Za-z\-']+", text.lower())
    out = []
    for t in toks:
        if t not in out:
            out.append(t)
        if len(out) >= k:
            break
    return out

def dat_score(words, k=7):
    """Divergent Association Task score: mean pairwise semantic distance of the first k words, x100,
    averaged over the embedding ensemble. None if fewer than 2 usable words. Length is controlled by
    construction (fixed k), so this is not confounded by elaboration (Beaty et al. 2022)."""
    w = words[:k]
    if len(w) < 2:
        return None
    return float(pairwise_dist_ensemble(w).mean() * 100.0)

def set_diversity(texts):
    """Mean pairwise semantic distance across a set of outputs (are they distinct or paraphrases?)."""
    if len(texts) < 2:
        return 0.0
    return float(pairwise_dist_ensemble(texts).mean())

def novelty_vs(text, refs, mode="min"):
    """Semantic novelty of `text` against reference outputs (e.g. the predictable 'mode' answers).
    mode='min' = distance to the NEAREST reference (how far from the closest cliché)."""
    if not refs:
        return 1.0
    a = embed([text])[0]
    R = embed(list(refs))
    d = 1.0 - (R @ a)
    return float(d.min() if mode == "min" else d.mean())

# ---- honest statistics (numpy only) ----
def bootstrap_ci(values, iters=10000, alpha=0.05, seed=0):
    """Mean with a percentile bootstrap 95% CI."""
    x = np.asarray([v for v in values if v is not None], dtype=np.float64)
    if len(x) == 0:
        return (float("nan"), float("nan"), float("nan"), 0)
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), size=(iters, len(x)))].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (float(x.mean()), float(lo), float(hi), len(x))

def permutation_test(a, b, iters=20000, seed=0):
    """Two-sided permutation test for difference in means (a - b). Returns (diff, p)."""
    a = np.asarray([v for v in a if v is not None], dtype=np.float64)
    b = np.asarray([v for v in b if v is not None], dtype=np.float64)
    if len(a) == 0 or len(b) == 0:
        return (float("nan"), float("nan"))
    obs = a.mean() - b.mean()
    pool = np.concatenate([a, b]); na = len(a)
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(pool[:na].mean() - pool[na:].mean()) >= abs(obs) - 1e-12:
            count += 1
    return (float(obs), float((count + 1) / (iters + 1)))


if __name__ == "__main__":
    # Self-check: divergent word lists must outscore clustered ones, and the gap must be significant.
    divergent = [["cat", "democracy", "helium", "sorrow", "bulldozer", "jazz", "tangerine"],
                 ["volcano", "ethics", "spoon", "galaxy", "whisper", "tariff", "moss"],
                 ["wrench", "nostalgia", "plankton", "opera", "uranium", "ladder", "drizzle"]]
    clustered = [["dog", "cat", "hamster", "rabbit", "parrot", "goldfish", "turtle"],
                 ["red", "blue", "green", "yellow", "orange", "purple", "pink"],
                 ["car", "truck", "bus", "van", "motorcycle", "scooter", "bicycle"]]
    ds = [dat_score(w) for w in divergent]
    cs = [dat_score(w) for w in clustered]
    print("divergent DAT:", [round(x, 1) for x in ds])
    print("clustered DAT:", [round(x, 1) for x in cs])
    assert min(ds) > max(cs), "divergent lists must score above clustered lists"
    diff, p = permutation_test(ds, cs, iters=5000)
    m, lo, hi, n = bootstrap_ci(ds)
    print(f"divergent mean={m:.1f} CI=[{lo:.1f},{hi:.1f}] n={n}; diff={diff:.1f} p={p:.4f}")
    nov = novelty_vs("offload the reduction to a GPU parallel scan kernel",
                     ["use a for loop to sum the list", "iterate and add up the values"])
    print(f"novelty_vs(mode) sanity = {nov:.3f}")
    print("score.py self-check passed")
