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
    Splits text into verifiable statements.
    Works for numbered lists, bullet points, separate lines, or sentences.
    Ensures user-typed custom claims (like 'MS Dhoni retired from IPL') are NEVER ignored.
    """
    raw_lines = text.split("\n")
    candidates = []
    
    for line in raw_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        # If line has numbering like "1. ", "2) ", strip it
        cleaned_line = re.sub(r'^\d+[.)]\s+', '', line_clean)
        cleaned_line = re.sub(r'^[•\-*]\s+', '', cleaned_line).strip()
        
        # If it's a multi-sentence line, split by periods
        if len(cleaned_line) > 120 and "." in cleaned_line:
            sents = re.split(r'(?<=[.!?])\s+', cleaned_line)
            for s in sents:
                if len(s.strip()) >= 15:
                    candidates.append(s.strip())
        else:
            if len(cleaned_line) >= 15:
                candidates.append(cleaned_line)

    claims = []
    for idx, cand in enumerate(candidates):
        # Skip purely decorative headers or bracketed notes
        if cand.startswith("(") and cand.endswith(")"):
            continue
        # Remove any internal annotations
        display_text = re.sub(r'\s*\([^)]*(?:Trap|trap|NOTE|Real Fact)[^)]*\)', '', cand).strip()
        if len(display_text) < 15:
            continue

        claims.append({
            "id": f"claim_{idx+1}",
            "claim_text": display_text,
            "type": "factual"
        })

    return claims


def extract_claims_with_llm(text: str, api_key: str = None, provider: str = "gemini") -> List[Dict[str, Any]]:
    """Extract claims via LLM. Falls back to heuristic on any failure."""
    prompt = (
        "You are an expert Fact-Checking AI. "
        "Extract every specific factual claim or statement from the document/text below. "
        "Include all claims about sports records, retirements, company statistics, money, dates, rankings, and historical facts. "
        "Return ONLY a JSON array. Each element: "
        '{"id":"claim_N","claim_text":"...","subject":"...","category":"..."}\n\n'
        f"Text to Extract From:\n\"\"\"\n{text[:8000]}\n\"\"\""
    )
    if api_key and provider == "gemini":
        import urllib.request
        for model in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1},
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    raw = re.sub(r'^```json\s*', '', raw)
                    raw = re.sub(r'\s*```$', '', raw)
                    parsed = json.loads(raw)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed
            except Exception:
                continue

    return extract_claims_heuristic(text)
