import streamlit as st
import time
import json
import os
import pandas as pd
from extractor import extract_text_from_pdf, extract_claims_heuristic, extract_claims_with_llm
from search_engine import live_web_search
from verifier import verify_claim, VERDICT_VERIFIED, VERDICT_INACCURATE, VERDICT_FALSE

# Page setup
st.set_page_config(
    page_title="Fact-Check Agent | Cog Culture Truth Layer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Sleek Dark Glassmorphism UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%);
        padding: 2.2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(129, 140, 248, 0.4);
        color: #A5B4FC;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    
    .status-badge {
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85rem;
    }
    
    .badge-verified {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .badge-inaccurate {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-false {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .engine-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .pill-gemini {
        background: rgba(59, 130, 246, 0.2);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    .pill-heuristic {
        background: rgba(148, 163, 184, 0.15);
        color: #CBD5E1;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Sample Document Generator
SAMPLE_TRAP_TEXT = """Global Artificial Intelligence & Tech Marketing Report 2026
Prepared for CogCulture Strategic Review

Key Quantitative Claims:
1. According to official corporate records, Apple Inc. was founded in the year 1995 in Silicon Valley by Mark Zuckerberg.
2. Microsoft Corporation achieved unprecedented growth as its market cap surpassed $12.5 Trillion USD in Q1 2026.
3. OpenAI's ChatGPT achieved 100 million monthly active users in January 2023, just two months after its initial launch.
4. Alphabet Inc. reported annual advertising revenue exceeding $950 Billion USD for the fiscal year 2023.
5. In 2024, Python achieved over 85% developer market share according to Stack Overflow developer surveys.
6. Virat Kohli has the most ODI centuries in international cricket history.
"""

# Check for secrets or env keys
secret_gemini_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""

# Persistent session state
if "doc_text" not in st.session_state:
    st.session_state["doc_text"] = ""

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/shield.png", width=64)
    st.title("Settings & Keys")
    st.caption("Cog Culture • Fact-Checking Truth Layer")

    st.markdown("### 🔑 Intelligence Engine")
    api_choice = st.radio(
        "Select Verification Mode",
        ["Gemini 1.5 Flash (AI Reasoning)", "Offline Heuristic Mode (Free & Instant)", "OpenAI"]
    )

    gemini_key = ""
    openai_key = ""
    tavily_key = ""

    if "Gemini" in api_choice:
        gemini_key = st.text_input(
            "Gemini API Key",
            value=secret_gemini_key,
            type="password",
            help="Using Gemini for multimodal deep reasoning and semantic claim extraction."
        )
        if gemini_key:
            st.success("🟢 Gemini API Key Active")
    elif api_choice == "OpenAI":
        openai_key = st.text_input("OpenAI API Key", type="password", help="Enter OpenAI API key")

    st.markdown("---")
    st.markdown("### 🌐 Web Search Settings")
    tavily_key = st.text_input("Tavily Search API Key (Optional)", type="password", help="Defaults to DuckDuckGo/Wikipedia if blank")

    st.markdown("---")
    st.markdown("### 📋 1-Click Trap Document Test")
    if st.button("Load Pre-set Trap Document", type="secondary", use_container_width=True):
        st.session_state["doc_text"] = SAMPLE_TRAP_TEXT
        if "verification_results" in st.session_state:
            del st.session_state["verification_results"]
        st.rerun()

    st.markdown("---")
    st.caption("Built for Cog Culture Assessment by **Aryan Dubey**")

# Main Header Banner
st.markdown("""
<div class="main-header">
    <div class="hero-badge">AI Truth Layer Agent</div>
    <h1 style="color: #FFFFFF; margin: 0; font-size: 2.2rem; font-weight: 800;">
        Automated Fact-Checking & Claim Verification
    </h1>
    <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 0.5rem; margin-bottom: 0;">
        Cross-reference marketing PDFs against live web intelligence. Automatically detect hallucinated stats, outdated metrics, and unverified claims.
    </p>
</div>
""", unsafe_allow_html=True)

# Document Input Section
col_upload, col_action = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "📄 Upload Marketing PDF for Fact-Checking",
        type=["pdf"],
        help="Upload any PDF to extract and verify claims against live web data"
    )

with col_action:
    st.write("Or evaluate immediately:")
    if st.button("⚡ Quick Test with Trap Document", use_container_width=True):
        st.session_state["doc_text"] = SAMPLE_TRAP_TEXT
        if "verification_results" in st.session_state:
            del st.session_state["verification_results"]
        st.rerun()

if uploaded_file is not None:
    extracted = extract_text_from_pdf(uploaded_file)
    if extracted:
        st.session_state["doc_text"] = extracted
        st.success(f" Successfully extracted {len(extracted)} characters from `{uploaded_file.name}`")
    else:
        st.error("Could not extract readable text from this PDF. Please check if it's scanned or password-protected.")

# If document text is loaded
if st.session_state["doc_text"]:
    doc_text = st.session_state["doc_text"]
    
    st.text_area("📄 Document Text Ready for Audit:", doc_text, height=140)

    # Big verification trigger button
    if st.button("🚀 Run Automated Truth Layer Verification", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        active_mode = "Gemini AI" if gemini_key else ("OpenAI" if openai_key else "Offline Heuristic")

        # Step 1: Extraction
        status_text.markdown(f"🔍 **Step 1/3: Extracting atomic claims using [{active_mode}]...**")
        claims = []
        if gemini_key:
            claims = extract_claims_with_llm(doc_text, api_key=gemini_key, provider="gemini")
        elif openai_key:
            claims = extract_claims_with_llm(doc_text, api_key=openai_key, provider="openai")
        
        if not claims:
            claims = extract_claims_heuristic(doc_text)

        progress_bar.progress(30)
        time.sleep(0.3)

        if not claims:
            st.warning("No verifiable quantitative claims or statistics detected in this document.")
        else:
            status_text.markdown(f"🌐 **Step 2/3: Identified {len(claims)} claims. Querying live web & running [{active_mode}] verification...**")
            
            results = []
            total_claims = len(claims)

            for idx, claim in enumerate(claims):
                c_text = claim.get("claim_text", "")
                used_engine = "Gemini 1.5 Flash" if gemini_key else ("OpenAI GPT-4o-mini" if openai_key else "Heuristic Rule-Engine")

                search_query = c_text[:120]
                web_evidence = live_web_search(search_query, tavily_api_key=tavily_key if tavily_key else None)
                
                # Primary verification (Gemini / OpenAI / Heuristic)
                verdict_data = verify_claim(
                    claim_text=c_text,
                    web_evidence=web_evidence,
                    gemini_api_key=gemini_key,
                    openai_api_key=openai_key
                )

                combined_item = {
                    "id": idx + 1,
                    "claim": c_text,
                    "verdict": verdict_data.get("verdict", VERDICT_FALSE),
                    "confidence": verdict_data.get("confidence_score", 85),
                    "real_facts": verdict_data.get("real_facts", "N/A"),
                    "explanation": verdict_data.get("explanation", ""),
                    "source_links": verdict_data.get("source_links", []),
                    "engine_used": used_engine
                }
                results.append(combined_item)
                
                cur_prog = 30 + int(70 * (idx + 1) / total_claims)
                progress_bar.progress(min(cur_prog, 100))
                time.sleep(0.2)

            status_text.success(f" Verification completed using **{active_mode}**!")
            progress_bar.progress(100)
            st.session_state["verification_results"] = results
            st.session_state["active_engine_name"] = active_mode

# Display Results if Available
if "verification_results" in st.session_state:
    results = st.session_state["verification_results"]
    active_engine = st.session_state.get("active_engine_name", "AI Truth Layer")

    st.markdown("---")
    
    # Header with Engine Badge
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader("📊 Verification Executive Summary")
    with col_t2:
        if "Gemini" in active_engine:
            st.markdown('<div style="text-align: right; padding-top: 10px;"><span class="engine-pill pill-gemini">⚡ Verified via Gemini 1.5 Flash</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: right; padding-top: 10px;"><span class="engine-pill pill-heuristic">⚙️ Verified via Heuristic Fallback</span></div>', unsafe_allow_html=True)

    total_c = len(results)
    verified_c = len([r for r in results if r["verdict"] == VERDICT_VERIFIED])
    inaccurate_c = len([r for r in results if r["verdict"] == VERDICT_INACCURATE])
    false_c = len([r for r in results if r["verdict"] == VERDICT_FALSE])

    # Metric Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Claims Audited", total_c)
    with col2:
        st.metric("✅ Verified Accurate", verified_c, delta=f"{int(verified_c/total_c*100)}%" if total_c else "0%")
    with col3:
        st.metric("⚠️ Inaccurate / Outdated", inaccurate_c, delta=f"-{int(inaccurate_c/total_c*100)}%" if total_c else "0%", delta_color="inverse")
    with col4:
        st.metric("❌ False / Fabricated", false_c, delta=f"-{int(false_c/total_c*100)}%" if total_c else "0%", delta_color="inverse")

    st.markdown("---")
    st.subheader("📑 Detailed Claim-by-Claim Truth Audit")

    # Filter selector
    filter_val = st.radio("Filter Claims by Status:", ["All Claims", "Verified Only", "Inaccurate Only", "False Only"], horizontal=True)

    for item in results:
        v = item["verdict"]
        if filter_val == "Verified Only" and v != VERDICT_VERIFIED:
            continue
        if filter_val == "Inaccurate Only" and v != VERDICT_INACCURATE:
            continue
        if filter_val == "False Only" and v != VERDICT_FALSE:
            continue

        if v == VERDICT_VERIFIED:
            badge_html = f'<span class="status-badge badge-verified">✅ VERIFIED ACCURATE ({item["confidence"]}%)</span>'
            border_c = "#10B981"
        elif v == VERDICT_INACCURATE:
            badge_html = f'<span class="status-badge badge-inaccurate">⚠️ INACCURATE / OUTDATED ({item["confidence"]}%)</span>'
            border_c = "#F59E0B"
        else:
            badge_html = f'<span class="status-badge badge-false">❌ FALSE / FABRICATED ({item["confidence"]}%)</span>'
            border_c = "#EF4444"

        engine_badge = f'<span class="engine-pill {"pill-gemini" if "Gemini" in item.get("engine_used", "") else "pill-heuristic"}">🔍 {item.get("engine_used", "Auditor")}</span>'

        sources_html = ""
        if item.get("source_links"):
            sources_html = "<br><b>Authoritative Grounding Sources:</b><br>" + "".join([
                f'<a href="{lnk}" target="_blank" style="color: #818CF8; margin-right: 12px; font-size: 0.85rem;">🔗 {lnk[:55]}...</a><br>'
                for lnk in item["source_links"]
            ])

        st.markdown(f"""
        <div style="background-color: #1E293B; border-left: 4px solid {border_c}; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.2rem; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <div>
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; margin-right: 8px;">CLAIM #{item['id']}</span>
                    {engine_badge}
                </div>
                {badge_html}
            </div>
            <div style="font-size: 1.05rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.8rem;">
                "{item['claim']}"
            </div>
            <div style="background-color: #0F172A; border-radius: 8px; padding: 0.85rem; margin-top: 0.5rem; font-size: 0.9rem;">
                <div style="color: #38BDF8; font-weight: 600; margin-bottom: 4px;">🎯 Real Facts / True Reference:</div>
                <div style="color: #E2E8F0; margin-bottom: 8px; font-weight: 500;">{item['real_facts']}</div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 6px;"><b>AI Audit Analysis:</b> {item['explanation']}</div>
                {sources_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Export Report
    st.markdown("### 📥 Export Audit Report")
    df_export = pd.DataFrame(results)
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV Audit Report",
        data=csv_data,
        file_name="CogCulture_FactCheck_Audit_Report.csv",
        mime="text/csv"
    )
