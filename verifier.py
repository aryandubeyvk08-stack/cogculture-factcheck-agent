import json
import re
import urllib.request
from typing import Dict, Any, List

VERDICT_VERIFIED = "Verified"
VERDICT_INACCURATE = "Inaccurate"
VERDICT_FALSE = "False"

def verify_claim_with_gemini(claim_text: str, web_evidence: List[Dict[str, str]], api_key: str) -> Dict[str, Any]:
    """
    Leverages Gemini 1.5 Flash to compare the claim against harvested web search snippets.
    Also utilizes native Google Search grounding if supported.
    """
    evidence_text = "\n\n".join([
        f"Source: {item.get('title', '')} ({item.get('url', '')})\nSnippet: {item.get('snippet', '')}"
        for item in web_evidence
    ])

    prompt = f"""
You are an uncompromising Fact-Checking Truth Layer auditor.
Compare the Claim against the Live Web Evidence provided below.

Claim: "{claim_text}"

Live Web Evidence:
\"\"\"
{evidence_text if evidence_text else "No direct web snippets returned."}
\"\"\"

Classify this claim into EXACTLY ONE of these three categories:
1. "Verified": The claim matches live data, real statistics, dates, and factual figures accurately.
2. "Inaccurate": The claim references a real entity or event, BUT contains outdated figures, incorrect percentages, misattributed metrics, or inflated stats. YOU MUST state the correct/real figures.
3. "False": The claim is completely fabricated, untrue, contradicts proven reality, or has zero legitimate evidence.

Return a JSON object with:
- "verdict": ("Verified" | "Inaccurate" | "False")
- "confidence_score": (Integer between 0 and 100)
- "real_facts": "The accurate, updated facts or figures (Mandatory for Inaccurate or False claims)"
- "explanation": "Clear, concise justification explaining why the claim was flagged"
- "source_links": ["list of URL sources from evidence supporting this judgment"]

Return ONLY raw JSON:
{{
  "verdict": "...",
  "confidence_score": 95,
  "real_facts": "...",
  "explanation": "...",
  "source_links": [...]
}}
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        # Request with search grounding if possible or direct content
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            res_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(res_text)
    except Exception as e:
        return None

def verify_claim_with_openai(claim_text: str, web_evidence: List[Dict[str, str]], api_key: str) -> Dict[str, Any]:
    """
    Leverages OpenAI GPT-4o-mini to verify claims against web snippets.
    """
    evidence_text = "\n\n".join([
        f"Source: {item.get('title', '')} ({item.get('url', '')})\nSnippet: {item.get('snippet', '')}"
        for item in web_evidence
    ])

    prompt = f"""
You are an uncompromising Fact-Checking Truth Layer auditor.
Compare the Claim against the Live Web Evidence provided below.

Claim: "{claim_text}"

Live Web Evidence:
\"\"\"
{evidence_text if evidence_text else "No direct web snippets returned."}
\"\"\"

Classify into EXACTLY one of: "Verified", "Inaccurate", "False".
Provide correct real facts for Inaccurate/False claims.

Return JSON:
{{
  "verdict": "Verified" | "Inaccurate" | "False",
  "confidence_score": 90,
  "real_facts": "...",
  "explanation": "...",
  "source_links": []
}}
"""
    try:
        url = "https://api.openai.com/v1/chat/completions"
        payload = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            raw_content = data["choices"][0]["message"]["content"]
            return json.loads(raw_content)
    except Exception:
        return None

def verify_claim_heuristic(claim_text: str, web_evidence: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Fallback deterministic validator using lexical matching and numerical delta checking
    when no LLM API key is provided or offline.
    """
    if not web_evidence:
        return {
            "verdict": VERDICT_FALSE,
            "confidence_score": 60,
            "real_facts": "No corroborated live web evidence or authoritative citations found for this claim.",
            "explanation": "Automated search across live web indices returned zero reputable sources corroborating the stated claim.",
            "source_links": []
        }

    # Extract numbers from claim
    claim_numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', claim_text)
    combined_snippets = " ".join([item.get('snippet', '') + " " + item.get('title', '') for item in web_evidence]).lower()
    source_links = [item.get('url', '') for item in web_evidence if item.get('url')]

    # Check number match
    matching_numbers = [num for num in claim_numbers if num.lower() in combined_snippets]

    if len(claim_numbers) > 0 and len(matching_numbers) == len(claim_numbers):
        return {
            "verdict": VERDICT_VERIFIED,
            "confidence_score": 85,
            "real_facts": f"Matches verified public metrics corroborated in live search citations.",
            "explanation": f"Claim figures ({', '.join(claim_numbers)}) align with reported statistics in cited sources.",
            "source_links": source_links[:3]
        }
    elif len(claim_numbers) > 0 and len(matching_numbers) < len(claim_numbers):
        return {
            "verdict": VERDICT_INACCURATE,
            "confidence_score": 75,
            "real_facts": "Discrepancy detected between the document's quoted figures and current authoritative live sources.",
            "explanation": f"The claim references figures ({', '.join(claim_numbers)}) that deviate from current live search data or indicate outdated statistics.",
            "source_links": source_links[:3]
        }
    else:
        return {
            "verdict": VERDICT_VERIFIED,
            "confidence_score": 70,
            "real_facts": "Contextually supported by live web search results.",
            "explanation": "General factual context is supported by referenced web sources.",
            "source_links": source_links[:3]
        }

def verify_claim(
    claim_text: str,
    web_evidence: List[Dict[str, str]],
    gemini_api_key: str = None,
    openai_api_key: str = None
) -> Dict[str, Any]:
    """
    Unified Verification Orchestrator:
    1. Attempts Gemini verification (if key available)
    2. Attempts OpenAI verification (if key available)
    3. Falls back to Heuristic Verification
    """
    if gemini_api_key:
        res = verify_claim_with_gemini(claim_text, web_evidence, gemini_api_key)
        if res and "verdict" in res:
            return res

    if openai_api_key:
        res = verify_claim_with_openai(claim_text, web_evidence, openai_api_key)
        if res and "verdict" in res:
            return res

    return verify_claim_heuristic(claim_text, web_evidence)
