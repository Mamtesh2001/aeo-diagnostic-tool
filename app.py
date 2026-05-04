import streamlit as st
import os
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# ── Ask Groq (LLaMA 3.3) ──────────────────────────────────────
def ask_groq(query):
    try:
        chat = groq_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"List the top 5 best products for: {query}. Give specific real brand names and product names only. Number them 1-5."
            }],
            model="llama-3.3-70b-versatile",
            max_tokens=500
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ── Ask Together AI (Mistral) ──────────────────────────────────
def ask_together(query):
    try:
        chat = groq_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"List the top 5 best products for: {query}. Give specific real brand names and product names only. Number them 1-5."
            }],
            model="llama-3.3-70b-versatile",
            max_tokens=500
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ── Score function ─────────────────────────────────────────────
def check_mention(product, response):
    if not product or not response:
        return False, 0
    product_lower = product.lower().strip()
    response_lower = response.lower()
    if product_lower in response_lower:
        lines = response_lower.split('\n')
        for i, line in enumerate(lines):
            if product_lower in line:
                return True, max(10 - i, 1)
        return True, 5
    return False, 0

# ── UI ─────────────────────────────────────────────────────────
st.set_page_config(page_title="AEO Diagnostic Tool", page_icon="🔍", layout="centered")

st.title("🔍 AEO Diagnostic Tool")
st.markdown("**See how your product ranks when AI assistants answer shopper questions.**")
st.divider()

col1, col2 = st.columns(2)
with col1:
    product = st.text_input("🛍️ Your Product Name", placeholder="e.g. Doctor's Best Magnesium")
with col2:
    query = st.text_input("🔎 Shopper Query", placeholder="e.g. best magnesium for seniors")

competitors = st.text_input(
    "🏁 Competitor names (optional, comma separated)",
    placeholder="e.g. Nature Made, Thorne, Garden of Life"
)

run = st.button("🚀 Run AEO Diagnostic", use_container_width=True, type="primary")

if run:
    if not query:
        st.warning("⚠️ Please enter a shopper query.")
    elif not product:
        st.warning("⚠️ Please enter your product name.")
    else:
        with st.spinner("🤖 Querying Groq (LLaMA) and Together AI (Mistral)... ~10 seconds"):
            groq_resp    = ask_groq(query)
            together_resp = ask_together(query)

        st.divider()
        st.subheader("📊 Report Card")

        results = {
            "🦙 Groq / LLaMA 3.3":          groq_resp,
            "♊ Groq / Gemma 2 9B": together_resp,
        }

        total_score = 0
        for ai_name, response in results.items():
            mentioned, score = check_mention(product, response)
            total_score += score
            status = "✅ Mentioned!" if mentioned else "❌ Not mentioned"
            with st.expander(f"{ai_name} — {status}", expanded=True):
                st.markdown(f"**Visibility Score:** {score}/10")
                st.markdown("**AI Response:**")
                st.info(response)

        # Overall score
        st.divider()
        max_possible = 20
        pct = int((total_score / max_possible) * 100)
        st.subheader(f"🏆 Overall AEO Score: {pct}/100")
        st.progress(pct / 100)

        if pct >= 60:
            st.success("✅ Great visibility! AI assistants know your product well.")
        elif pct >= 30:
            st.warning("⚠️ Moderate visibility. Work on your product's online presence.")
        else:
            st.error("❌ Low visibility. AI assistants are not recommending your product yet.")

        # Competitor analysis
        if competitors:
            st.divider()
            st.subheader("🏁 Competitor Visibility")
            comp_list = [c.strip() for c in competitors.split(",") if c.strip()]

            col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
            col_h1.markdown("**Product**")
            col_h2.markdown("**Groq**")
            col_h3.markdown("**Together AI**")

            for comp in comp_list:
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.markdown(f"**{comp}**")
                m1, _ = check_mention(comp, groq_resp)
                m2, _ = check_mention(comp, together_resp)
                c2.markdown("✅" if m1 else "❌")
                c3.markdown("✅" if m2 else "❌")

st.divider()
st.caption("Built with Groq/LLaMA 3.3 · Groq/Gemma 2 — AEO Diagnostic Tool")