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
    # Try PyMuPDF first
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

    # Fallback to pypdf
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

def clean_sentence_units(text: str) -> List[str]:
    """Cleans lines and extracts coherent sentences or numbered list items."""
    # Split by numbered lists like "1. ", "2. " or sentence punctuation
    raw_lines = text.split("\n")
    cleaned_blocks = []
    current_block = ""

    for line in raw_lines:
        line_s = line.strip()
        if not line_s:
            continue
        
        # Check if it starts a new numbered item or bullet
        if re.match(r'^\d+[\.\)]\s+', line_s) or re.match(r'^[•\-\*]\s+', line_s):
            if current_block:
                cleaned_blocks.append(current_block)
            current_block = line_s
        else:
            if current_block:
                current_block += " " + line_s
            else:
                current_block = line_s

    if current_block:
        cleaned_blocks.append(current_block)

    # Further break down non-bullet blocks by period if they are long
    final_sentences = []
    for block in cleaned_blocks:
        if re.match(r'^\d+[\.\)]\s+', block):
            final_sentences.append(block)
        else:
            sents = re.split(r'(?<=[.!?])\s+', block)
            final_sentences.extend(sents)

    return final_sentences

def extract_claims_heuristic(text: str) -> List[Dict[str, Any]]:
    """
    Robust rule-based claim extractor identifying sentences with figures, statistics,
    percentages, dates, financial currencies, and factual claims.
    Filters out parenthetical notes or metadata.
    """
    candidates = clean_sentence_units(text)
    claims = []

    stat_patterns = [
        r'\b\d+(\.\d+)?%\b',
        r'[\$€£₹]\s*\d+([,\.]\d+)?\s*(billion|million|trillion|k|m|b)?\b',
        r'\b\d+([,\.]\d+)?\s*(billion|million|trillion|thousand|users|customers|queries)\b',
        r'\b(in|by|since|year|during)\s+(19\d\d|20\d\d)\b',
        r'\b(increased|decreased|grew|fell|exceeded|reached|surpassed|founded)\b',
        r'\b(number\s+one|leading|first|fastest|market\s+share)\b'
    ]
    combined_pattern = re.compile('|'.join(stat_patterns), re.IGNORECASE)

    claim_id = 1
    for block in candidates:
        clean_block = block.strip()
        # Skip explanatory bracket annotations like "(Intentional Trap: ...)"
        if clean_block.startswith("(") and clean_block.endswith(")"):
            continue
        if len(clean_block) < 30 or len(clean_block) > 500:
            continue

        if combined_pattern.search(clean_block):
            # Clean off leading numbers like "1. "
            display_text = re.sub(r'^\d+[\.\)]\s+', '', clean_block)
            # Remove any trailing internal annotations
            display_text = re.sub(r'\s*\([^)]*Trap:[^)]*\)', '', display_text).strip()

            claims.append({
                "id": f"claim_{claim_id}",
                "claim_text": display_text,
                "type": "statistical/quantitative"
            })
            claim_id += 1

    return claims

def extract_claims_with_llm(text: str, api_key: str = None, provider: str = "gemini") -> List[Dict[str, Any]]:
    """Extracts atomic, verifiable claims using LLM API."""
    prompt = f"""
You are an expert Fact-Checking AI and Truth Layer Auditor.
Analyze the following document text and extract all specific, verifiable factual claims.
Focus on:
1. Statistics, percentages, ratios, metrics.
2. Market share figures, valuations, revenue, financial figures.
3. Dates, timelines, milestones, historical facts.
4. Technical specifications or product capabilities.

For each claim, return a JSON list of objects with:
- "id": "claim_N"
- "claim_text": The exact or atomic claim stated in the text
- "subject": The entity or subject of the claim
- "category": ("statistic", "financial", "timeline", "market_share", "technical")

Document Text:
\"\"\"
{text[:8000]}
\"\"\"

Return ONLY valid JSON matching this schema:
[
  {{"id": "claim_1", "claim_text": "...", "subject": "...", "category": "..."}}
]
"""
    if api_key and provider == "gemini":
        try:
            import urllib.request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
            }).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                res_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(res_text)
        except Exception:
            pass

    return extract_claims_heuristic(text)
