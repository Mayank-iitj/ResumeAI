import re
from typing import List

SECTION_HEADERS = ["summary", "profile", "experience", "education", "skills", "projects", "certifications"]

HEADER_PATTERN = re.compile(r"^(?:" + "|".join([h.capitalize() + r"|" + h.upper() for h in SECTION_HEADERS]) + r")(?:\s*[:|-])?\s*$")

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_into_lines(text: str) -> List[str]:
    return [l.strip() for l in text.splitlines() if l.strip()]

def detect_sections(raw_text: str) -> dict:
    lines = split_into_lines(raw_text)
    sections = {}
    current = "other"
    for line in lines:
        if HEADER_PATTERN.match(line):
            normalized = line.lower().split()[0]
            current = normalized if normalized in SECTION_HEADERS else "other"
            if current not in sections:
                sections[current] = []
        sections.setdefault(current, []).append(line)
    # join
    for k,v in sections.items():
        sections[k] = "\n" + "\n".join(v)
    return sections

def extract_years_of_experience(text: str) -> float:
    # Very heuristic: count distinct years mentioned and approximate duration.
    years = re.findall(r"(19|20)\d{2}", text)
    unique_years = sorted(set(int(y) for y in years))
    if len(unique_years) >= 2:
        span = unique_years[-1] - unique_years[0]
        if span < 0:
            span = 0
        return span if span <= 50 else 0
    # fallback: look for patterns like 'X years'
    m = re.findall(r"(\d+\.?\d*)\s+years", text.lower())
    if m:
        return max(float(x) for x in m)
    return 0.0
