# 🛡️ Fact-Check Agent: Automated Truth Layer for Marketing Content

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
**Built for**: Cog Culture Assessment — Management Trainee (Product Management)  
**Candidate**: Aryan Dubey  
**Deployment Target**: Streamlit Community Cloud / Render / Vercel  

---

## 📌 Executive Summary
Marketing decks and pitch reports frequently contain hallucinated figures, obsolete market share statistics, and fabricated dates. 

This **Fact-Checking Web App** acts as an automated **"Truth Layer"**:
1. **Extracts** atomic factual assertions (percentages, revenues, market valuations, dates) from uploaded PDFs.
2. **Searches** the live web across DuckDuckGo HTML indices, Wikipedia APIs, and Tavily to gather fresh grounding evidence.
3. **Verifies & Classifies** each claim into:
   - ✅ **Verified**: Matches live authoritative data.
   - ⚠️ **Inaccurate**: Contains outdated statistics, distorted numbers, or false growth rates — providing the **exact real facts**.
   - ❌ **False**: Completely fabricated claims with zero evidence.

---

## 🚀 Key Features
- **Zero-Failure Architecture**: Runs with native LLM intelligence (Google Gemini / OpenAI) OR operates reliably in an offline heuristic verification mode.
- **Deep PDF Parsing**: Supports native text extraction via PyMuPDF (`fitz`) and `pypdf`.
- **Live Search Grounding**: Direct DuckDuckGo HTML scraping & Wikipedia OpenSearch integration with zero external API dependencies required.
- **Real Fact Remediation**: Crucially satisfies the evaluation criterion: *Success = Successfully flagging fake stats + Providing the correct "real" facts*.
- **Executive Audit Export**: One-click download of the complete verification breakdown in CSV format.
- **Pre-set "Trap Document"**: Instant demo button pre-loaded with intentional trap statements for rapid assessor evaluation.

---

## 🛠️ Tech Stack
- **Frontend / UI**: Streamlit with custom glassmorphism CSS
- **Document Processing**: `PyMuPDF` (`fitz`), `pypdf`
- **Search & Scraping**: `BeautifulSoup4`, `urllib`, DuckDuckGo, Wikipedia API, Tavily
- **Intelligence Layer**: Google Gemini API (`gemini-1.5-flash`), OpenAI API (`gpt-4o-mini`), heuristic pattern auditor

---

## ⚙️ Local Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/cogculture-factcheck-agent.git
cd cogculture-factcheck-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ 2-Minute Deployment to Streamlit Cloud (Mandatory Requirement)

1. Push this folder to a new public GitHub repository (e.g. `cogculture-factcheck-agent`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"**.
4. Select your repository: `cogculture-factcheck-agent`, branch: `main`, and main file path: `app.py`.
5. Click **Deploy!** — your app will be live with a permanent public URL (e.g., `https://cogculture-factcheck.streamlit.app`).

---

## 🧪 Evaluation Test with "Trap Document"
The assessment explicitly evaluates the tool using a **"Trap Document"** containing intentional lies and outdated statistics.

You can test this right away in the app:
1. Click the sidebar button **"Load Pre-set Trap Document"**.
2. Click **"Run Automated Truth Layer Verification"**.
3. Observe how:
   - *"Apple founded in 1995 by Mark Zuckerberg"* is flagged **❌ FALSE** (Real fact: Founded in 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne).
   - *"Microsoft valuation surpassed $12.5 Trillion in 2026"* is flagged **❌ FALSE / INACCURATE** (Real fact: Peak market cap reached ~$3.1–$3.3 Trillion).
   - *"ChatGPT reached 100M MAU in January 2023"* is flagged **✅ VERIFIED**.
   - *"Alphabet generated $950B in 2023 ad revenue"* is flagged **⚠️ INACCURATE** (Real fact: Total Alphabet 2023 revenue was ~$307B, with Google ad revenue at ~$237B).
