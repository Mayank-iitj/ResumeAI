import re
from typing import Tuple

PII_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)[\s-]?)?\d{3,4}[\s-]?\d{4}"),
    "linkedin": re.compile(r"https?://(www\.)?linkedin\.com/[^\s]+"),
    "github": re.compile(r"https?://(www\.)?github\.com/[^\s]+"),
}

def anonymize(text: str) -> Tuple[str, dict]:
    replacements = {}
    anonymized = text
    for label, pattern in PII_PATTERNS.items():
        matches = pattern.findall(anonymized)
        if matches:
            for i, m in enumerate(matches):
                token = f"<{label.upper()}_{i}>"
                anonymized = anonymized.replace(m, token)
            replacements[label] = matches
    # naive name removal (first line often contains name) if single words capitalized
    lines = anonymized.splitlines()
    if lines:
        first = lines[0]
        if len(first.split()) <= 4 and first == first.title():
            lines[0] = "<NAME>"
            replacements["name"] = [first]
        anonymized = "\n".join(lines)
    return anonymized, replacements
