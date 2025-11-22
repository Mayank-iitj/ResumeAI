from typing import Dict, List
import re
import logging
import os
from functools import lru_cache

from .config import SKILL_KEYWORDS, SKILL_SYNONYMS, SPACY_MODEL, EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

# Lazy holders; avoid heavy model load at import (improves cold start time).
_NLP = None
_EMBED = None

FAST_MODE = os.getenv("FAST_MODE", "false").lower() == "true"

def get_nlp():
    global _NLP
    if FAST_MODE:
        if _NLP is None:
            try:
                import spacy
                _NLP = spacy.blank("en")
            except Exception:
                logger.warning("Failed to init blank spaCy model in FAST_MODE.")
        return _NLP
    if _NLP is None:
        try:
            import spacy
            _NLP = spacy.load(SPACY_MODEL)
        except Exception:
            logger.warning("spaCy model not found; attempting download or fallback.")
            try:
                import spacy
                from spacy.cli import download
                download(SPACY_MODEL)
                _NLP = spacy.load(SPACY_MODEL)
            except Exception:
                logger.warning("Falling back to blank English model.")
                import spacy
                _NLP = spacy.blank("en")
    return _NLP

def get_embed_model():
    global _EMBED
    if FAST_MODE:
        return None
    if _EMBED is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBED = SentenceTransformer(EMBEDDING_MODEL_NAME)
        except Exception:
            _EMBED = None
            logger.warning("SentenceTransformer model unavailable; embeddings disabled.")
    return _EMBED

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
    for canonical, syns in SKILL_SYNONYMS.items():
        for syn in syns:
            if re.search(r"\b" + re.escape(syn) + r"\b", lower_text):
                found.add(canonical)
    return sorted(found)

def extract_entities(text: str) -> Dict[str, List[str]]:
    if FAST_MODE:
        return {}
    nlp = get_nlp()
    if nlp is None:
        return {}
    doc = nlp(text)
    entities: Dict[str, List[str]] = {}
    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)
    return entities

@lru_cache(maxsize=2048)
def _embed_single(text: str):
    model = get_embed_model()
    if model is None:
        return None
    return model.encode([text], show_progress_bar=False)[0]

def embed_texts(texts: List[str]):
    model = get_embed_model()
    if model is None:
        return None
    return [_embed_single(t) for t in texts]
