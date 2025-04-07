# ESG Risk Assessment Streamlit App (ChatGPT-powered frontend)

import streamlit as st
import pandas as pd
import openai
import io
from datetime import datetime

# --- Configuration ---
st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")
st.title("ESG Risk Rating Tool (ChatGPT-Powered)")

# --- Load API Key from secrets.toml ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- User Input ---
st.markdown("Enter supplier name(s) and spend to generate a full ESG risk report.")
with st.form("esg_form"):
    suppliers_data = []
    for i in range(10):
        cols = st.columns([4, 2])
        name = cols[0].text_input(f"Supplier {i+1} Name")
        spend = cols[1].number_input(f"Spend (£) for Supplier {i+1}", min_value=0.0, step=100.0)
        if name:
            suppliers_data.append({"name": name, "spend": spend})
    submitted = st.form_submit_button("Run ESG Assessment")

# --- Prompt Template ---
base_prompt = """
You are an expert ESG risk assessment analyst. Run a comprehensive ESG analysis for the following suppliers using real data and web sentiment where possible. Use UK Government carbon conversion categories, apply relevant UNSPSC-based emissions, and include ESG dimensions in the report.

For each supplier, provide:
- Supplier Name
- Annual Spend
- UNSPSC Code & Description (best match)
- UK Gov Category + Emissions Category
- Scope 1 & Scope 2 emissions (based on spend)
- Total Estimated Carbon Emissions
- Environmental Risk Score and Explanation
- Social Risk Score and Explanation
- Governance Risk Score and Explanation
- Supplier Ownership & Diversity Status
- Board Diversity
- Sedex Membership
- Third-party Manufacturing Sites
- Modern Slavery Statement / Reported Factory Conditions / Whistleblowing
- Media Sentiment (with Examples)
- Science-Based Targets (SBTi) Status
- London Living Wage Accreditation
- B Corp Certification
- Fair Payment Code Signatory
- Confidence Level & Justification
- Recommended Buyer Actions
- Overall RAG Rating (Green, Amber, Red)

Provide all this in table format for Excel export. Color code rows using the RAG status.
"""

# --- Processing Function ---
def run_esg_chatgpt(suppliers):
    supplier_text = "\n".join([f"{s['name']}, £{s['spend']}" for s in suppliers])
    prompt = base_prompt + f"\n\nSuppliers:\n{supplier_text}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a sustainability analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message['content']

# --- Generate Excel File ---
def generate_excel_from_text(text):
    rows = [r.strip() for r in text.strip().split("\n") if r]
    headers = [h.strip() for h in rows[0].split("|") if h]
    data = [[c.strip() for c in row.split("|") if c] for row in rows[2:]]
    df = pd.DataFrame(data, columns=headers)

    # Apply RAG coloring and save
    def rag_color(val):
        if "Green" in val:
            return 'background-color: lightgreen'
        elif "Amber" in val:
            return 'background-color: orange'
        elif "Red" in val:
            return 'background-color: lightcoral'
        else:
            return ''

    styled = df.style.applymap(rag_color, subset=[col for col in df.columns if 'RAG' in col])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        styled.to_excel(writer, index=False, sheet_name="ESG Report")
    buffer.seek(0)
    return buffer

# --- Run and Display ---
if submitted and suppliers_data:
    with st.spinner("Running ESG risk assessments using GPT..."):
        report_text = run_esg_chatgpt(suppliers_data)
        st.markdown("### ESG Risk Report")
        st.text_area("Raw Output", report_text, height=400)

        file_buffer = generate_excel_from_text(report_text)
        st.download_button(
            label="📥 Download ESG Report (Excel)",
            data=file_buffer,
            file_name="esg_risk_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
