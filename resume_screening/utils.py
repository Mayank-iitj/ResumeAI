import re
from typing import List, Tuple
from datetime import datetime
from dateutil import parser as dateparser

SECTION_HEADERS = ["summary", "profile", "experience", "education", "skills", "projects", "certifications"]

HEADER_PATTERN = re.compile(r"^(?:" + "|".join([h.capitalize() + r"|" + h.upper() for h in SECTION_HEADERS]) + r")(?:\s*[:|-])?\s*$")
DATE_RANGE_PATTERN = re.compile(r"(?P<start>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\s*(?:19|20)\d{2}|present|current)\s*(?:-|to|–|—)\s*(?P<end>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\s*(?:19|20)\d{2}|present|current)", re.IGNORECASE)

MONTH_MAP = {m.lower(): i for i, m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Sept","Oct","Nov","Dec"], start=1)}


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
    for k, v in sections.items():
        sections[k] = "\n" + "\n".join(v)
    return sections


def _parse_date(token: str) -> datetime | None:
    token = token.strip().lower()
    if token in {"present", "current"}:
        return datetime.utcnow()
    # Add month if missing for consistency
    try:
        if re.match(r"^(19|20)\d{2}$", token):
            return datetime(int(token), 7, 1)
        # Try month-year separated
        parts = token.split()
        if len(parts) == 2 and parts[0] in MONTH_MAP:
            month = MONTH_MAP[parts[0]]
            year = int(parts[1])
            return datetime(year, month, 1)
        return dateparser.parse(token, default=datetime(2000,1,1))
    except Exception:
        return None


def extract_years_of_experience(text: str) -> float:
    ranges: List[Tuple[datetime, datetime]] = []
    for m in DATE_RANGE_PATTERN.finditer(text):
        start_raw = m.group("start")
        end_raw = m.group("end")
        start_dt = _parse_date(start_raw)
        end_dt = _parse_date(end_raw)
        if start_dt and end_dt and end_dt >= start_dt:
            ranges.append((start_dt, end_dt))

    if ranges:
        # Merge overlapping ranges to avoid double counting
        ranges.sort(key=lambda r: r[0])
        merged = []
        cur_start, cur_end = ranges[0]
        for s, e in ranges[1:]:
            if s <= cur_end:
                if e > cur_end:
                    cur_end = e
            else:
                merged.append((cur_start, cur_end))
                cur_start, cur_end = s, e
        merged.append((cur_start, cur_end))
        total_days = sum((e - s).days for s, e in merged)
        years = total_days / 365.25
        # Cap unrealistic spans
        if years > 60:
            years = 0
        return round(years, 2)

    # Fallback 1: explicit "X years" mentions
    mentions = [float(x) for x in re.findall(r"(\d+\.?\d*)\s+years", text.lower())]
    if mentions:
        val = max(mentions)
        return val if val <= 60 else 0

    # Fallback 2: detect unique years and infer span
    years_found = sorted(set(int(y) for y in re.findall(r"(19|20)\d{2}", text)))
    if len(years_found) >= 2:
        span = years_found[-1] - years_found[0]
        return span if 0 <= span <= 60 else 0

    return 0.0
