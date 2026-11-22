<div align="center">

# 🛡️ Fact-Check Agent: Automated "Truth Layer" for Marketing Content

**Cog Culture Assessment Deliverable — Management Trainee (Product Management)**  
*Engineered by **Aryan Vijay Dubey***

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cogculture-factcheck-agent-bc38mkk95wvbxqv38sdbkh.streamlit.app/)
[![Loom Demo](https://img.shields.io/badge/Demo_Video-Loom-625DF5?logo=loom&logoColor=white)](https://www.loom.com/share/db63011e950342e7a359fe1e57d28ff2)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🚀 **Live Deployed Web App**](https://cogculture-factcheck-agent-bc38mkk95wvbxqv38sdbkh.streamlit.app/) • [🎥 **Watch 30s Loom Demo**](https://www.loom.com/share/db63011e950342e7a359fe1e57d28ff2) • [📑 **Part 1 GEO Strategy Deck**](https://github.com/aryandubeyvk08-stack/cogculture-factcheck-agent/tree/main)

---

</div>

## 📌 Executive Summary & Product Vision

Marketing presentations, whitepapers, and pitch decks frequently suffer from **hallucinated metrics, obsolete market valuations, and unverified growth statistics**. When published, these inaccuracies damage brand credibility and mislead stakeholders.

This **Fact-Checking Web App** serves as an autonomous, enterprise-grade **"Truth Layer"**:
1. **Extracts** atomic factual assertions (percentages, revenues, market valuations, historical dates, and superlative world records) from uploaded marketing PDFs.
2. **Cross-References** each assertion against live web data, authoritative knowledge graphs, Wikipedia OpenSearch APIs, and search indices.
3. **Classifies & Remediates**:
   - ✅ **Verified Accurate**: Grounded in authoritative real-time facts.
   - ⚠️ **Inaccurate / Outdated**: Catches metric exaggerations and **provides the exact, verified real-world facts**.
   - ❌ **False / Fabricated**: Pinpoints intentional hallucinations, entity falsehoods, and ungrounded statements.

---

## 🏗️ Technical Architecture & Pipeline

```
[ Uploaded PDF / Text ]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│  Stage 1: Multi-Modal Claim Extractor                  │
│  • Dual-engine PyMuPDF (fitz) + pypdf text parser      │
│  • Superlative & Quantitative Regex Extraction Engine  │
│  • Dynamic Gemini LLM Atomic Statement Chunking       │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│  Stage 2: Live Grounding & Evidence Harvesting         │
│  • Live Web Search (DuckDuckGo HTML Scraping)          │
│  • Real-Time Wikipedia OpenSearch REST API             │
│  • Tavily Intelligence Fallback                        │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│  Stage 3: Dual-Engine Verification & Remediation       │
│  ├─ Mode A: Google Gemini 1.5 Flash (Deep AI Reasoning)│
│  └─ Mode B: Offline Deterministic Heuristic Engine     │
│             (Zero-Downtime Guarantee if Quotas End)    │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│  Stage 4: Executive Audit Dashboard                    │
│  • Status Pill Badges & Live Engine Telemetry          │
│  • Direct Grounding Citation Links                     │
│  • One-Click CSV Compliance Audit Report Export        │
└────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Highlights & Engineering USPs

- 🛡️ **Zero-Failure Architecture**: Solves the real-world evaluator dilemma where third-party API quotas get exhausted. Evaluators can run the app in **Gemini 1.5 Flash Reasoning Mode** or switch to **Offline Heuristic Mode** for instant, token-free verification.
- 🎯 **Strict Evaluation Metric Alignment**: Specifically fulfills the assessment mandate:  
  $$\text{Success} = \text{Successfully flagging fake stats} + \text{Providing the correct "real" facts}$$
- 🏏 **Broad Factual Scope**: Handles both quantitative corporate statistics ($12.5T valuation, 85% developer share) and superlative world records (e.g. *Virat Kohli holding the world record for 50 ODI centuries*).
- ⚡ **Streamlit Cloud Native**: Zero local-machine dependencies, runs on Python 3.14 on Linux headless containers.

---

## 🧪 Evaluation Test with "Trap Document"

The assessment explicitly evaluates the tool using a **"Trap Document"** containing intentional lies and outdated statistics.

You can test this right inside the live web app using the **`⚡ Quick Test with Trap Document`** button:

| # | Statement in Document | Status | Truth Layer Finding / Real Fact Provided |
| :-: | :--- | :---: | :--- |
| **1** | *"Apple Inc. was founded in the year 1995 in Silicon Valley by Mark Zuckerberg."* | ❌ **FALSE** | **Real Fact:** Apple was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne. Mark Zuckerberg founded Facebook in 2004. |
| **2** | *"Microsoft market cap surpassed $12.5 Trillion USD in Q1 2026."* | ❌ **FALSE** | **Real Fact:** Gross statistical inflation. Microsoft's peak valuation reached ~$3.1–$3.3 Trillion USD. No public company in history has reached $12.5T. |
| **3** | *"OpenAI's ChatGPT achieved 100M MAU in January 2023, just two months after launch."* | ✅ **VERIFIED** | **Real Fact:** Precisely matches verified UBS and Reuters historical adoption records (fastest-growing consumer app in history). |
| **4** | *"Alphabet reported annual ad revenue exceeding $950 Billion USD for FY 2023."* | ⚠️ **INACCURATE** | **Real Fact:** Alphabet's total FY23 revenue was $307.4B (with Google Advertising accounting for $237.8B), not $950B. |
| **5** | *"In 2024, Python achieved over 85% developer market share according to Stack Overflow."* | ⚠️ **INACCURATE** | **Real Fact:** According to official Stack Overflow Developer Surveys, Python usage is ~51%, and it is not the sole language used in AI. |
| **6** | *"Virat Kohli has the most ODI centuries in international cricket history."* | ✅ **VERIFIED** | **Real Fact:** Verified record. Virat Kohli holds 50 ODI centuries, surpassing Sachin Tendulkar's 49 during the 2023 ICC World Cup. |

---

## 🛠️ Tech Stack & Dependencies

- **Frontend & Dashboard**: [Streamlit](https://streamlit.io/) with custom dark glassmorphism CSS
- **Document Ingestion**: `PyMuPDF` (`fitz`), `pypdf`
- **Search & Web Grounding**: `BeautifulSoup4`, `urllib`, Wikipedia OpenSearch API, DuckDuckGo
- **AI Intelligence**: Google Gemini 1.5 Flash (`generativelanguage.googleapis.com`), OpenAI API (`gpt-4o-mini`)
- **Data & Export**: `pandas` (CSV Report Generation)

---

## 💻 Local Installation & Setup

If you wish to run the app locally:

```bash
# 1. Clone the repository
git clone https://github.com/aryandubeyvk08-stack/cogculture-factcheck-agent.git
cd cogculture-factcheck-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit Web Application
streamlit run app.py
```
The app will immediately open at `http://localhost:8501`.

---

## 📁 Repository Structure

```
├── app.py                     # Streamlit application dashboard & UI cards
├── extractor.py               # Robust claim & quantitative sentence extractor
├── search_engine.py           # DuckDuckGo HTML & Wikipedia API search aggregator
├── verifier.py                # Dual-Engine auditor (Gemini LLM + Heuristic Fallback)
├── requirements.txt           # Deployment dependency specifications
├── .gitignore                 # Excludes caches, venv, and environment files
├── CogCulture_Trap_Document_Test.pdf   # Pre-generated benchmark test PDF
└── README.md                  # Comprehensive documentation & evaluation guide
```

---

## 👤 Author & Candidate Profile

**Aryan Vijay Dubey**  
- **Role Applied**: Management Trainee — Product Management  
- **Organization**: Cog Culture (`Cog Digital (P) Ltd`)  
- **GitHub**: [@aryandubeyvk08-stack](https://github.com/aryandubeyvk08-stack)  
- **Live App**: [https://cogculture-factcheck-agent-bc38mkk95wvbxqv38sdbkh.streamlit.app/](https://cogculture-factcheck-agent-bc38mkk95wvbxqv38sdbkh.streamlit.app/)
- **Demo Video**: [Loom Walkthrough](https://www.loom.com/share/db63011e950342e7a359fe1e57d28ff2)
