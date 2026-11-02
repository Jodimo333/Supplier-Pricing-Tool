import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# web page layout
st.set_page_config(page_title="Pricing tool", layout="wide")
st.title("Supplier Price Update Tool")
st.markdown("Easily recalculates retail prices and export PDF quotations")

# to prevent reloading the csv on every button click
@st.cache_data
def load_data():
    return pd.read_csv('price_updates.csv')

# edge cases (ensure the user runs the pricing pipeline first)
try:
    df = load_data()
except FileNotFoundError:
    st.error("not found, run pricing.py")
    st.stop()

# overview of business impact
total_products = len(df)
total_saved = df['Profit_Saved_Per_Unit'].sum().round(2)

# display metrics using layout columns
col1, col2, col3 = st.columns(3)
col1.metric("Items Requiring Price Update", total_products)
col2.metric("Total Margin Protected ($)", f"${total_saved}")
col3.metric("Biggest Price Drop Anomaly", f"${df['Cost_Differences'].min()}")

st.subheader("Actionable Price Updates")
# filter dataframe to display only the most critical commercial columns
display_df = df[['Internal_SKU', 'Category', 'Current_Cost', 'Clean_New_Cost', 'New_Retail_Price', 'Profit_Saved_Per_Unit']]
st.dataframe(display_df, use_container_width=True)

st.subheader("Top 5 Products - Highest Profit Saved Per Unit")
# isolating the 5 revenue drivers to help sales team prioritize updates
top_5 = df.nlargest(5, 'Profit_Saved_Per_Unit')

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(top_5['Internal_SKU'], top_5['Profit_Saved_Per_Unit'], color='green')
ax.set_ylabel("Profit Saved ($)")
ax.set_xlabel("Product SKU")
st.pyplot(fig)

# generate the pdf file
def generate_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Automated Price Quotation Form (PQF)", ln=True, align='C')
    pdf.cell(200, 10, txt="Confidential - Internal Use Only", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 10, "SKU", border=1)
    pdf.cell(40, 10, "Category", border=1)
    pdf.cell(40, 10, "New Cost", border=1)
    pdf.cell(40, 10, "New Retail Price", border=1)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for index, row in dataframe.head(30).iterrows():
        pdf.cell(40, 10, str(row['Internal_SKU']), border=1)
        pdf.cell(40, 10, str(row['Category']), border=1)
        pdf.cell(40, 10, str(row['Clean_New_Cost']), border=1)
        pdf.cell(40, 10, str(row['New_Retail_Price']), border=1)
        pdf.ln()

    pdf.output("Price_Quotation.pdf")

# export
st.subheader("Export Business Quotation")
st.markdown("Generate a PDF ready to be sent to sales teams or clients.")

# trigger pdf generation only upon user request
if st.button("Generate PDF Quotation (PQF)"):
    generate_pdf(df)
    st.success("PDF Generated Successfully!")

    # expose the generated pdf for direct download via browser
    with open("Price_Quotation.pdf", "rb") as pdf_file:
        st.download_button(
            label="Download PDF Document",
            data=pdf_file,
            file_name="Price_Quotation.pdf",
            mime="application/pdf"
        )
