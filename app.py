import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from pdf_engine import build_pdf_document
from config import SUPPLIER_DETAILS, BANK_DETAILS_PRIMARY, BANK_DETAILS_SECONDARY

st.set_page_config(page_title="MR MOBILE SA - Enterprise Portal", layout="wide")

# Initialize Session State for Invoice Database and Tab Management
if "invoices_db" not in st.session_state:
    st.session_state.invoices_db = [
        {
            "doc_num": "PI-2026-1002-02",
            "client_name": "Twenty-Five Star (Pty) Ltd",
            "trading_name": "Pedros Distribution Centre DBN",
            "invoice_total": 535854.00,
            "deposit_required": 267927.00,
            "status": "Outstanding",
            "amount_paid": 0.00,
            "balance_outstanding": 535854.00,
            "date": "2026-10-02"
        }
    ]

st.title("MR MOBILE SA — Commercial Document & Invoicing Engine")

# Multi-tab layout configuration
tab1, tab2 = st.tabs(["📄 Document Generator", "📊 Invoice Tracking Dashboard"])

# ==========================================
# TAB 1: DOCUMENT GENERATOR PORTAL
# ==========================================
with tab1:
    st.subheader("Create & Configure Commercial Document")
    
    # Dynamically fetch latest US$/ZAR market rate with fallback
    def get_live_usd_zar_rate():
        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
            if response.status_code == 200:
                rates = response.json().get("rates", {})
                return float(rates.get("ZAR", 18.25))
        except Exception:
            pass
        return 18.25

    base_usd_zar = get_live_usd_zar_rate()
    adjusted_usd_zar = base_usd_zar * 1.035  # Adding 3.5% for bank charges

    col_a, col_b = st.columns(2)
    with col_a:
        doc_type = st.selectbox("Document Type", ["PRO FORMA INVOICE", "TAX INVOICE", "QUOTATION"])
        shipping_mode = st.selectbox("Shipping Mode", ["Sea Freight", "Air Freight", "Express Courier"])
    with col_b:
        doc_date = st.date_input("Document Date", value=datetime.today())
        doc_num = st.text_input("Document Number", value="PI-2026-1002-03")

    col_c, col_d = st.columns(2)
    with col_c:
        due_date = st.text_input("Due Date", value="Immediate (Upon Receipt)")
    with col_d:
        validity = st.text_input("Validity", value="30 Days")

    # Display Dynamic Exchange Rate on Screen
    st.markdown("---")
    st.markdown(
        f"**Live US$/ZAR Market Rate (incl. 3.5% Bank Charges):** "
        f"<span style='color:#B91C1C; font-size:16px;'><b>R {adjusted_usd_zar:,.4f}</b></span> "
        f"<font size=2 color='#64748B'>(Base: R {base_usd_zar:,.4f} + 3.5% Admin)</font>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Client Details
    st.markdown("### Client & Billing Details")
    col_e, col_f = st.columns(2)
    with col_e:
        client_name = st.text_input("Client Name", value="Twenty-Five Star (Pty) Ltd")
        trading_name = st.text_input("Trading Name", value="Pedros Distribution Centre DBN")
        reg_vat = st.text_input("Co. Reg & VAT", value="Co. Reg: 2022/686760/07 | VAT: 4690317583")
    with col_f:
        reg_address = st.text_input("Reg Address", value="33 Aiken Street, Port Shepstone, KZN, 4240")
        del_address = st.text_input("Delivery Address", value="4-6 Suzuka Road, Westmead, Pinetown, 3608")

    # Line Items
    st.markdown("### Commercial Line-Item Specification")
    num_items = st.number_input("How many products / line items?", min_value=1, max_value=10, value=1)

    products = []
    grand_excl = 0.0
    grand_incl = 0.0

    for i in range(int(num_items)):
        st.markdown(f"#### Item #{i+1}")
        sku = st.text_input(f"SKU / Item Code #{i+1}", value="600ml Food Flask")
        desc = st.text_area(f"Bespoke Description #{i+1}", value="Plain SS304 Body Configuration. Landed DDP Pinetown.")
        qty = st.number_input(f"Quantity (Units) #{i+1}", min_value=1, value=3000)
        unit_price = st.number_input(f"Unit Price Excl. VAT (R) #{i+1}", min_value=0.0, value=155.32, format="%.2f")
        
        net_subtotal = qty * unit_price
        total_incl = net_subtotal * 1.15  # 15% VAT
        
        grand_excl += net_subtotal
        grand_incl += total_incl

        products.append({
            "SKU": sku,
            "Description": desc,
            "Qty": qty,
            "Unit Price (Excl)": unit_price,
            "Net Subtotal (Excl)": net_subtotal,
            "Total Price (Incl)": total_incl
        })

    tranche1_incl = grand_incl * 0.50

    # Compile Invoice Data
    invoice_data = {
        "document_type": doc_type,
        "shipping_mode": shipping_mode,
        "invoice_date": doc_date,
        "invoice_num": doc_num,
        "due_date": due_date,
        "validity": validity,
        "exchange_rate_display": f"R {adjusted_usd_zar:,.4f}",
        "bank_details_primary": BANK_DETAILS_PRIMARY,
        "bank_details_secondary": BANK_DETAILS_SECONDARY,
        "client": {
            "client_name": client_name,
            "trading_name": trading_name,
            "reg_vat": reg_vat,
            "reg_address": reg_address,
            "del_address": del_address
        },
        "products": products
    }

    if st.button("Generate & Download PDF Invoice", type="primary"):
        try:
            pdf_buffer = build_pdf_document(invoice_data)
            
            # Register or update invoice in session database
            existing_idx = next((idx for idx, inv in enumerate(st.session_state.invoices_db) if inv["doc_num"] == doc_num), None)
            new_inv_record = {
                "doc_num": doc_num,
                "client_name": client_name,
                "trading_name": trading_name,
                "invoice_total": grand_incl,
                "deposit_required": tranche1_incl,
                "status": "Outstanding",
                "amount_paid": 0.00,
                "balance_outstanding": grand_incl,
                "date": str(doc_date)
            }
            
            if existing_idx is not None:
                st.session_state.invoices_db[existing_idx] = new_inv_record
            else:
                st.session_state.invoices_db.append(new_inv_record)

            st.success("PDF generated successfully and recorded in dashboard!")
            st.download_button(
                label="📥 Click Here to Download Generated PDF",
                data=pdf_buffer,
                file_name=f"{doc_num}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

# ==========================================
# TAB 2: INVOICE TRACKING DASHBOARD
# ==========================================
with tab2:
    st.subheader("Enterprise Financial Tracking Dashboard")
    st.markdown("Monitor all issued commercial documents, track payment clearances, and inspect outstanding balances in real time.")

    if not st.session_state.invoices_db:
        st.info("No invoices generated yet.")
    else:
        # Convert to DataFrame for metrics & display
        df_invoices = pd.DataFrame(st.session_state.invoices_db)

        # Metrics Overview
        total_billed = df_invoices["invoice_total"].sum()
        total_collected = df_invoices["amount_paid"].sum()
        total_outstanding = df_invoices["balance_outstanding"].sum()

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Billed Portfolio", f"R {total_billed:,.2f}")
        col_m2.metric("Total Collected", f"R {total_collected:,.2f}")
        col_m3.metric("Total Outstanding Balance", f"R {total_outstanding:,.2f}")

        st.markdown("---")
        st.markdown("### Detailed Invoice Ledger & Payment Manager")

        updated_db = []
        for idx, inv in enumerate(st.session_state.invoices_db):
            with st.expander(f"Invoice: {inv['doc_num']} | Client: {inv['client_name']} ({inv['trading_name']}) - [{inv['status']}]"):
                col_i1, col_i2, col_i3 = st.columns(3)
                
                with col_i1:
                    st.text(f"Document No: {inv['doc_num']}")
                    st.text(f"Client: {inv['client_name']}")
                    st.text(f"Trading Name: {inv['trading_name']}")
                    st.text(f"Issue Date: {inv['date']}")

                with col_i2:
                    st.text(f"Invoice Total (Incl.): R {inv['invoice_total']:,.2f}")
                    st.text(f"50% Deposit Req.: R {inv['deposit_required']:,.2f}")

                with col_i3:
                    new_status = st.selectbox(
                        "Payment Status", 
                        ["Outstanding", "Partially Paid", "Paid in Full"], 
                        index=["Outstanding", "Partially Paid", "Paid in Full"].index(inv["status"]),
                        key=f"status_{idx}"
                    )
                    
                    max_val = float(inv["invoice_total"])
                    new_amount_paid = st.number_input(
                        "Amount Paid (R)", 
                        min_value=0.0, 
                        max_value=max_val, 
                        value=float(inv["amount_paid"]), 
                        step=1000.0,
                        key=f"paid_{idx}"
                    )

                new_balance = max_val - new_amount_paid
                st.markdown(f"**Calculated Balance Outstanding:** <span style='color:#B91C1C;'><b>R {new_balance:,.2f}</b></span>", unsafe_allow_html=True)

                updated_db.append({
                    "doc_num": inv["doc_num"],
                    "client_name": inv["client_name"],
                    "trading_name": inv["trading_name"],
                    "invoice_total": inv["invoice_total"],
                    "deposit_required": inv["deposit_required"],
                    "status": new_status,
                    "amount_paid": new_amount_paid,
                    "balance_outstanding": new_balance,
                    "date": inv["date"]
                })

        # Save updates back to session state
        st.session_state.invoices_db = updated_db

        # Summary Data Table View
        st.markdown("---")
        st.markdown("### Master Ledger Summary Table")
        display_df = pd.DataFrame(st.session_state.invoices_db)
        display_df.columns = ["Invoice No", "Client Name", "Trading Name", "Total (R)", "Deposit (R)", "Status", "Paid (R)", "Outstanding (R)", "Date"]
        st.dataframe(display_df, use_container_width=True)
