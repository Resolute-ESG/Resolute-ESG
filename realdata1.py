# ESG Risk Assessment Streamlit App (ChatGPT-Powered)

import streamlit as st
import openai
import pandas as pd
import io
from fpdf import FPDF

# --- CONFIGURATION ---
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Store this securely in Streamlit secrets or environment

st.set_page_config(page_title="ChatGPT ESG Risk Tool", layout="wide")
st.title("ESG Risk Assessment Tool (Powered by GPT-4)")

st.markdown("""
Enter supplier names and spend values. This app sends the data to GPT-4 to generate ESG insights including:
- Carbon impact (kg CO₂e) and scope estimates
- Diversity and ownership status
- ESG risks, RAG rating, confidence level
- Sentiment examples and recommended actions
- Output in Excel or PDF format
""")

# --- SUPPLIER INPUT FORM ---
suppliers = []
with st.form("input_form"):
    for i in range(5):
        cols = st.columns([3, 2])
        name = cols[0].text_input(f"Supplier {i+1} Name")
        spend = cols[1].number_input(f"Spend (£) for Supplier {i+1}", min_value=0.0, step=100.0)
        if name:
            suppliers.append({"name": name, "spend": spend})
    submitted = st.form_submit_button("Run ESG Assessment")

# --- API CALL TEMPLATE ---
def get_esg_analysis(supplier_name, spend):
    prompt = f"""
Run the full ESG risk rating using the previously agreed format.
Supplier: {supplier_name}, Spend: £{spend}.
Include:
- Scope 1 & 2 emissions
- ESG (Environmental, Social, Governance) risk scores and RAG rating
- Diversity status (ownership and board)
- B Corp, SBTi, LLW, Sedex, Fair Payment Code status
- Confidence level with justification
- Sentiment analysis with examples
- Recommended actions for procurement
Return results in structured format.
"""
    chat = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an ESG risk rating assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return chat['choices'][0]['message']['content']

# --- PROCESS INPUT ---
report_data = []
if submitted:
    for s in suppliers:
        response = get_esg_analysis(s["name"], s["spend"])
        report_data.append({"Supplier": s["name"], "Spend": s["spend"], "GPT-4 ESG Report": response})
    df = pd.DataFrame(report_data)
    st.success("Report generated. Choose your download format.")
    st.dataframe(df)

    # --- EXPORT OPTIONS ---
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Excel", csv, file_name="esg_report.csv")

    with col2:
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'ESG Risk Assessment Report', ln=True, align='C')
            def supplier_block(self, entry):
                self.set_font('Arial', '', 10)
                self.multi_cell(0, 8, f"Supplier: {entry['Supplier']}\nSpend: £{entry['Spend']}\n{entry['GPT-4 ESG Report']}", border=0)
                self.ln(2)

        pdf = PDF()
        pdf.add_page()
        for record in report_data:
            pdf.supplier_block(record)
        buffer = io.BytesIO()
        pdf.output(buffer)
        st.download_button("Download PDF", buffer.getvalue(), file_name="esg_report.pdf", mime="application/pdf")
else:
    if submitted:
        st.warning("Please provide at least one supplier name.")
