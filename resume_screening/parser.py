import pdfplumber
import docx
from pathlib import Path
from typing import Tuple
from .utils import clean_text, detect_sections

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def read_pdf(path: Path) -> str:
    text = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text)

def read_docx(path: Path) -> str:
    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)

def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def parse_file(path_str: str) -> Tuple[str, dict]:
    path = Path(path_str)
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    if ext == ".pdf":
        raw = read_pdf(path)
    elif ext == ".docx":
        raw = read_docx(path)
    else:
        raw = read_txt(path)
    cleaned = clean_text(raw)
    sections = detect_sections(raw)
    return cleaned, sections
