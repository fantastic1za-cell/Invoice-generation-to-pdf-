import streamlit as st
from datetime import datetime
from pdf_engine import build_pdf_document
from config import SUPPLIER_DETAILS, BANK_DETAILS_PRIMARY, BANK_DETAILS_SECONDARY

st.set_page_config(page_title="MR MOBILE SA - Document Generator", layout="centered")

st.title("Document Generation Portal")

# 1. Document Configuration
doc_type = st.selectbox("Document Type", ["PRO FORMA INVOICE", "TAX INVOICE", "QUOTATION"])
shipping_mode = st.selectbox("Shipping Mode", ["Sea Freight", "Air Freight", "Express Courier"])

col1, col2 = st.columns(2)
with col1:
    doc_date = st.date_input("Document Date", value=datetime.today())
with col2:
    doc_num = st.text_input("Document Number", value="DOC-2026-1002-02")

due_date = st.text_input("Due Date", value="Immediate (Upon Receipt)")
validity = st.text_input("Validity", value="30 Days")

# Banking Account Selector aligned with interface specifications
st.markdown("### Banking Account Selection")
bank_selection = st.selectbox(
    "Select Receiving Bank Account",
    options=[
        f"Primary Acc: {BANK_DETAILS_PRIMARY['account_number']} ({BANK_DETAILS_PRIMARY['account_type']})",
        f"Secondary Acc: {BANK_DETAILS_SECONDARY['account_number']} ({BANK_DETAILS_SECONDARY['account_type']})"
    ],
    index=0
)
selected_bank = BANK_DETAILS_PRIMARY if "Primary" in bank_selection else BANK_DETAILS_SECONDARY

# Exchange Rate Display Field (Informational only, not used in calculation)
st.markdown("### Exchange Rate Display")
usd_zar_rate = st.text_input("Current US$/ZAR Market Rate (Display Only)", value="R 18.25")

# 2. Client Details Section
st.markdown("### Client & Billing Details")
client_name = st.text_input("Client Name", value="Twenty-Five Star (Pty) Ltd")
trading_name = st.text_input("Trading Name", value="Pedros Distribution Centre DBN")
reg_vat = st.text_input("Co. Reg & VAT", value="Co. Reg: 2022/686760/07 | VAT: 4690317583")
reg_address = st.text_input("Reg Address", value="33 Aiken Street, Port Shepstone, KZN, 4240")
del_address = st.text_input("Delivery Address", value="4-6 Suzuka Road, Westmead, Pinetown, 3608")

# 3. Line Items Section
st.markdown("### Commercial Line-Item Specification")
num_items = st.number_input("How many products / line items?", min_value=1, max_value=10, value=1)

products = []
for i in range(int(num_items)):
    st.markdown(f"#### Item #{i+1}")
    sku = st.text_input(f"SKU / Item Code #{i+1}", value="600ml Food Flask")
    desc = st.text_area(f"Bespoke Description #{i+1}", value="Plain SS304 Body Configuration. Landed DDP Pinetown.")
    qty = st.number_input(f"Quantity (Units) #{i+1}", min_value=1, value=3000)
    unit_price = st.number_input(f"Unit Price Excl. VAT (R) #{i+1}", min_value=0.0, value=155.32, format="%.2f")
    
    net_subtotal = qty * unit_price
    total_incl = net_subtotal * 1.15  # 15% VAT
    
    products.append({
        "SKU": sku,
        "Description": desc,
        "Qty": qty,
        "Unit Price (Excl)": unit_price,
        "Net Subtotal (Excl)": net_subtotal,
        "Total Price (Incl)": total_incl
    })

# Compile Data Payload
invoice_data = {
    "document_type": doc_type,
    "shipping_mode": shipping_mode,
    "invoice_date": doc_date,
    "invoice_num": doc_num,
    "due_date": due_date,
    "validity": validity,
    "selected_bank": selected_bank,
    "usd_zar_display_rate": usd_zar_rate,
    "client": {
        "client_name": client_name,
        "trading_name": trading_name,
        "reg_vat": reg_vat,
        "reg_address": reg_address,
        "del_address": del_address
    },
    "products": products
}

if st.button("Generate & Download PDF Invoice"):
    try:
        pdf_buffer = build_pdf_document(invoice_data)
        st.success("PDF generated successfully!")
        st.download_button(
            label="Download PDF Document",
            data=pdf_buffer,
            file_name=f"{doc_num}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
