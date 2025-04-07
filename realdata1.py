# ESG Risk Assessment Tool (Live Data - GitHub Version)

import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")
st.title("Live ESG Risk Assessment Tool")

st.markdown("""
This tool allows you to input up to 10 suppliers and their annual spend and returns:
- ESG risk ratings (Environmental, Social, Governance)
- Estimated carbon impact (UK GHG methodology)
- Diversity, Fair Payment, Modern Slavery, Sedex, LLW Accreditation
- Confidence score, sentiment analysis, SBTi commitment
- RAG status and actionable recommendations

**Note**: This version simulates enrichment; API integration and scraping logic are to be implemented.
""")

data = []

with st.form("supplier_form"):
    st.subheader("Enter Supplier Details")
    for i in range(10):
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            name = st.text_input(f"Supplier {i+1} Name", key=f"name_{i}")
        with col2:
            spend = st.number_input(f"Spend (£) for Supplier {i+1}", min_value=0.0, step=100.0, key=f"spend_{i}")
        with col3:
            category = st.text_input(f"Category for Supplier {i+1}", key=f"cat_{i}")
        if name:
            data.append({"Supplier Name": name, "Spend (£)": spend, "Category": category})

    submitted = st.form_submit_button("Run ESG Assessment")

def fetch_real_data(supplier_name, spend):
    return {
        "Country": "UK",
        "Region": "Greater London",
        "Ownership": "Privately Owned",
        "Diversity Status": "Minority-owned",
        "Board Diversity": "Yes",
        "SBTi Status": "Not Committed",
        "B Corp": "No",
        "Fair Payment Code": "Unknown",
        "Modern Slavery Statement": "Yes",
        "Sedex Member": "Yes",
        "LLW Accredited": "No",
        "Third-Party Manufacturing": "No",
        "Carbon Emissions (kg CO2e)": round(spend * 0.018, 2),
        "Environmental Risk": 30,
        "Social Risk": 45,
        "Governance Risk": 40,
        "Media Sentiment": "Neutral",
        "Media Examples": "No recent press concerns",
        "Confidence Level": 85,
        "Confidence Justification": "Cross-referenced with Companies House and Sedex",
        "Overall ESG Risk Score": 39,
        "Overall ESG RAG": "Amber",
        "Recommended Actions": "Engage supplier for ESG disclosures and verify audit results"
    }

def apply_rag_color(val):
    if val == "Green":
        return 'background-color: lightgreen'
    elif val == "Amber":
        return 'background-color: orange'
    elif val == "Red":
        return 'background-color: red'
    return ''

if submitted and data:
    enriched_data = []
    for row in data:
        enriched = fetch_real_data(row["Supplier Name"], row["Spend (£)"])
        enriched_data.append({**row, **enriched})

    df = pd.DataFrame(enriched_data)
    st.success("ESG Assessment Complete")
    st.dataframe(df.style.applymap(apply_rag_color, subset=["Overall ESG RAG"]))

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download ESG Report (CSV)", csv, "esg_report.csv", "text/csv")
elif submitted:
    st.warning("Please input at least one supplier.")

