from typing import List, Tuple, Dict
import math

try:
    from .nlp_extractor import embed_texts
except Exception:  # pragma: no cover
    embed_texts = lambda x: None  # type: ignore


def cosine(a, b):
    if a is None or b is None:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def responsibilities_similarity(responsibilities: List[str], experience_bullets: List[str]) -> Dict:
    """Compute average similarity between JD responsibilities and candidate experience bullets.

    Returns a dict with average similarity and matched pairs (best bullet per responsibility).
    """
    if not responsibilities or not experience_bullets:
        return {"average_similarity": 0.0, "pairs": []}

    resp_emb = embed_texts(responsibilities)
    exp_emb = embed_texts(experience_bullets)
    if resp_emb is None or exp_emb is None:
        return {"average_similarity": 0.0, "pairs": []}

    pairs: List[Tuple[str, str, float]] = []
    sims = []
    for i, r_vec in enumerate(resp_emb):
        best_sim = -1.0
        best_bullet = ""
        for j, e_vec in enumerate(exp_emb):
            sim = cosine(r_vec, e_vec)
            if sim > best_sim:
                best_sim = sim
                best_bullet = experience_bullets[j]
        sims.append(best_sim)
        pairs.append((responsibilities[i], best_bullet, round(best_sim, 4)))

    avg = sum(sims) / len(sims) if sims else 0.0
    return {"average_similarity": round(avg, 4), "pairs": pairs}
