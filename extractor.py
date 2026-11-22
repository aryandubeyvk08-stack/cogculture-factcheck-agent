import re
import json
from typing import List, Dict, Any

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_text_from_pdf(pdf_file) -> str:
    """Extracts raw text from a PDF file-like object or path."""
    text = ""
    if fitz:
        try:
            if hasattr(pdf_file, "read"):
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                pdf_file.seek(0)
            else:
                doc = fitz.open(pdf_file)
            for page in doc:
                text += page.get_text() + "\n"
            if text.strip():
                return text.strip()
        except Exception:
            pass
    if pypdf:
        try:
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            if hasattr(pdf_file, "seek"):
                pdf_file.seek(0)
            if text.strip():
                return text.strip()
        except Exception:
            pass
    return text.strip()


def extract_claims_heuristic(text: str) -> List[Dict[str, Any]]:
    """
    Rule-based claim extractor. Identifies sentences containing:
      - numbers, percentages, currency, dates, magnitudes
      - superlatives / record claims (most, highest, fastest, largest, etc.)
      - named entities with factual assertions
    Skips short lines, headers, and parenthetical annotations.
    """
    # Split into candidate sentences
    raw_lines = text.split("\n")
    blocks = []
    cur = ""
    for line in raw_lines:
        s = line.strip()
        if not s:
            continue
        if re.match(r'^\d+[.)]\s+', s) or re.match(r'^[•\-*]\s+', s):
            if cur:
                blocks.append(cur)
            cur = s
        else:
            cur = (cur + " " + s) if cur else s
    if cur:
        blocks.append(cur)

    # Further split long non-numbered blocks by sentence boundaries
    sentences = []
    for b in blocks:
        if re.match(r'^\d+[.)]\s+', b):
            sentences.append(b)
        else:
            sentences.extend(re.split(r'(?<=[.!?])\s+', b))

    # Patterns that indicate a verifiable factual claim
    CLAIM_PATTERNS = re.compile(
        r'|'.join([
            r'\b\d+(\.\d+)?%',                          # 85%, 51.3%
            r'[\$€£₹]\s*\d+',                           # $950, €100
            r'\b\d[\d,]*\s*(billion|million|trillion|thousand|users|customers)',
            r'\b(in|by|since|during)\s+(19|20)\d\d\b',   # in 2023, by 2024
            r'\b(increased|decreased|grew|fell|exceeded|reached|surpassed|founded|launched|achieved|reported|raised)\b',
            r'\b(most|highest|fastest|largest|biggest|lowest|first|longest|record|leading|number.one)\b',
        ]),
        re.IGNORECASE,
    )

    claims = []
    claim_id = 1
    for sent in sentences:
        clean = sent.strip()
        # skip annotations like "(Intentional Trap: ...)"
        if clean.startswith("(") and clean.endswith(")"):
            continue
        if len(clean) < 25 or len(clean) > 600:
            continue

        if CLAIM_PATTERNS.search(clean):
            # strip leading "1. " numbering
            display = re.sub(r'^\d+[.)]\s+', '', clean)
            # strip trailing "(Trap: ...)" annotations
            display = re.sub(r'\s*\([^)]*(?:Trap|trap|NOTE)[^)]*\)', '', display).strip()
            if len(display) < 20:
                continue
            claims.append({
                "id": f"claim_{claim_id}",
                "claim_text": display,
                "type": "factual",
            })
            claim_id += 1

    return claims


def extract_claims_with_llm(text: str, api_key: str = None, provider: str = "gemini") -> List[Dict[str, Any]]:
    """Extract claims via LLM. Falls back to heuristic on any failure."""
    prompt = (
        "You are an expert Fact-Checking AI. "
        "Extract every specific, verifiable factual claim from the document below. "
        "Include claims about statistics, money, dates, records, rankings, and historical facts. "
        "Return ONLY a JSON array. Each element: "
        '{"id":"claim_N","claim_text":"...","subject":"...","category":"..."}\n\n'
        f"Document:\n\"\"\"\n{text[:8000]}\n\"\"\""
    )
    if api_key and provider == "gemini":
        import urllib.request
        for model in ["gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1},
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # strip markdown fences if present
                    raw = re.sub(r'^```json\s*', '', raw)
                    raw = re.sub(r'\s*```$', '', raw)
                    parsed = json.loads(raw)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed
            except Exception:
                continue

    # fallback
    return extract_claims_heuristic(text)
