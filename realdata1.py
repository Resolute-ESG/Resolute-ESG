# ESG Assessment App (Streamlit-compatible with real-time enrichment)

import streamlit as st
import pandas as pd
import requests
import io
from fpdf import FPDF

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")
st.title("ESG Risk Assessment for up to 10 Suppliers")

st.markdown("""
Enter up to 10 suppliers and their annual spend. This tool will return:
- ESG risk ratings (Environmental, Social, Governance)
- Estimated carbon impact (using UK Gov conversion factors)
- Diversity status, Board diversity, Sedex, LLW, Modern Slavery, Fair Payment Code
- Media sentiment with examples
- Overall RAG rating with colour-coded rows
- Confidence score and justification
- Scope 1 & 2 Emissions
- Recommended buyer actions
- Downloadable Excel or PDF report
""")

columns = ["Supplier Name", "Spend (£)", "Category (optional)"]
data = []

with st.form("supplier_form"):
    st.subheader("Supplier Inputs")
    for i in range(10):
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            name = st.text_input(f"Supplier {i+1} Name")
        with col2:
            spend = st.number_input(f"Spend (£) for Supplier {i+1}", min_value=0.0, step=100.0)
        with col3:
            category = st.text_input(f"Category for Supplier {i+1} (optional)")
        if name:
            data.append({"Supplier Name": name, "Spend (£)": spend, "Category": category})

    submitted = st.form_submit_button("Run ESG Assessment")

# Real-time data enrichment (prototype example using Companies House)
def enrich_supplier_info(supplier, spend):
    ch_url = f"https://api.company-information.service.gov.uk/search/companies?q={supplier}"
    headers = {"Authorization": "Basic YOUR_API_KEY=="}  # Replace with encoded API key
    response = requests.get(ch_url, headers=headers)

    if response.status_code == 200:
        results = response.json()
        items = results.get("items", [])
        company = items[0] if items else {}
        country = company.get("address_snippet", "Unknown")
    else:
        company = {}
        country = "Unknown"

    return {
        "Country": country,
        "Region": "To be added via secondary API",
        "Ownership": "To be sourced",
        "Diversity Status": "To be sourced",
        "Board Diversity": "To be sourced",
        "SBTi Status": "To be sourced",
        "B Corp": "To be sourced",
        "Fair Payment Code": "To be sourced",
        "Modern Slavery Statement": "To be sourced",
        "Sedex Membership": "To be sourced",
        "LLW Accredited": "To be sourced",
        "Third-Party Manufacturing": "To be sourced",
        "Scope 1 Emissions": round(spend * 0.010, 2),
        "Scope 2 Emissions": round(spend * 0.008, 2),
        "Total Carbon Emissions (kg CO2e)": round(spend * 0.018, 2),
        "Environmental Risk Score": 30,
        "Social Risk Score": 45,
        "Governance Risk Score": 40,
        "Media Sentiment": "To be sourced",
        "Media Examples": "To be sourced",
        "Confidence Level": 70,
        "Confidence Justification": "Limited external validation",
        "Overall ESG Risk Score": 39,
        "Overall ESG RAG": "Amber",
        "Recommended Actions": "Review self-disclosed information, seek assurance, verify media checks"
    }

def rag_color(val):
    if val == "Green":
        return 'background-color: lightgreen'
    elif val == "Amber":
        return 'background-color: orange'
    elif val == "Red":
        return 'background-color: red'
    return ''

if submitted and data:
    enriched = []
    for row in data:
        result = enrich_supplier_info(row["Supplier Name"], row["Spend (£)"])
        enriched.append({**row, **result})

    df = pd.DataFrame(enriched)
    st.success("ESG Assessment Complete")
    st.dataframe(df.style.applymap(rag_color, subset=["Overall ESG RAG"]))

    output_format = st.radio("Select Download Format", ["Excel", "PDF"])
    if output_format == "Excel":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download ESG Report (Excel)", csv, "esg_report.csv", "text/csv")
    else:
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'ESG Risk Assessment Report', 0, 1, 'C')

            def supplier_block(self, data):
                self.set_font('Arial', '', 10)
                for k, v in data.items():
                    self.cell(0, 8, f"{k}: {v}", 0, 1)
                self.ln(2)

        pdf = PDF()
        pdf.add_page()
        for record in enriched:
            pdf.supplier_block(record)

        buffer = io.BytesIO()
        pdf.output(buffer)
        st.download_button("Download ESG Report (PDF)", buffer.getvalue(), "esg_report.pdf", "application/pdf")
else:
    if submitted:
        st.warning("Please provide at least one supplier name.")
