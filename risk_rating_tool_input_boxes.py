
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")

st.title("ESG Risk Assessment Tool")
st.markdown("Enter up to 10 suppliers and their spend. The tool will simulate ESG risk scoring based on mock logic.")

# Create input fields for 10 suppliers
supplier_inputs = []
for i in range(1, 11):
    st.subheader(f"Supplier {i}")
    name = st.text_input(f"Supplier Name {i}", key=f"name_{i}")
    spend = st.number_input(f"Spend (£) {i}", min_value=0, step=1000, key=f"spend_{i}")
    if name:
        supplier_inputs.append({"Supplier Name": name, "Spend (£)": spend})

# Proceed if any suppliers were entered
if supplier_inputs:
    df = pd.DataFrame(supplier_inputs)

    # Sample ESG Scoring Logic (Mock) for demo purposes
    def assess_risk(row):
        score = 0
        if row["Spend (£)"] > 1000000:
            score += 1
        if "green" in row["Supplier Name"].lower() or "eco" in row["Supplier Name"].lower():
            score += 1
        if "oil" in row["Supplier Name"].lower() or "chemical" in row["Supplier Name"].lower():
            score -= 2

        if score >= 2:
            return "Low"
        elif score >= 0:
            return "Medium"
        else:
            return "High"

    df["ESG Risk Rating"] = df.apply(assess_risk, axis=1)

    st.success("Suppliers assessed successfully!")
    st.dataframe(df)

    # Download button
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ESG Assessment')
    st.download_button(label="Download ESG Risk Report",
                       data=output.getvalue(),
                       file_name="ESG_Risk_Report.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
