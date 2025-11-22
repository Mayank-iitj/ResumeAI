from typing import Dict, List
import re
import logging

from .config import SKILL_KEYWORDS, SKILL_SYNONYMS, SPACY_MODEL, EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

try:
    import spacy
    _NLP = spacy.load(SPACY_MODEL)
except Exception:
    logger.warning("spaCy model not found; attempting to download or using blank model.")
    try:
        import spacy
        from spacy.cli import download
        download(SPACY_MODEL)
        _NLP = spacy.load(SPACY_MODEL)
    except Exception:
        logger.warning("Falling back to blank English model.")
        import spacy
        _NLP = spacy.blank("en")

try:
    from sentence_transformers import SentenceTransformer
    _EMBED = SentenceTransformer(EMBEDDING_MODEL_NAME)
except Exception:
    _EMBED = None
    logger.warning("SentenceTransformer model not available; embeddings disabled.")

LOWER_SKILLS = [s.lower() for s in SKILL_KEYWORDS]

def normalize_skill(skill: str) -> str:
    skill_l = skill.lower()
    for canonical, syns in SKILL_SYNONYMS.items():
        if skill_l == canonical or skill_l in syns:
            return canonical
    return skill_l

def extract_skills(text: str) -> List[str]:
    found = set()
    lower_text = text.lower()
    for kw in LOWER_SKILLS:
        if re.search(r"\b" + re.escape(kw) + r"\b", lower_text):
            found.add(normalize_skill(kw))
    # synonyms pass
    for canonical, syns in SKILL_SYNONYMS.items():
        for syn in syns:
            if re.search(r"\b" + re.escape(syn) + r"\b", lower_text):
                found.add(canonical)
    return sorted(found)

def extract_entities(text: str) -> Dict[str, List[str]]:
    doc = _NLP(text)
    entities: Dict[str, List[str]] = {}
    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)
    return entities

def embed_texts(texts: List[str]):
    if _EMBED is None:
        return None
    return _EMBED.encode(texts, show_progress_bar=False)
