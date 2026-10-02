# ==============================================================================
# SCRIPT NAME: app.py
# TIMESTAMP: 2026-10-02 23:12:00 SAST
# STATUS: DIRECT JS AUTO-DOWNLOAD INJECTION & REFINED INTERFACE
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
import math
import base64
from datetime import datetime
from pdf_engine import build_pdf_document
from config import SUPPLIER_DETAILS, BANK_DETAILS_PRIMARY, BANK_DETAILS_SECONDARY

# 1. Page Configuration
st.set_page_config(
    page_title="Mr Mobile SA - Invoice Generator",
    page_icon="mmsalogo.png.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "invoices_db" not in st.session_state:
    st.session_state.invoices_db = [
        {
            "doc_num": "PI-2026-1002-03",
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

if "client_database" not in st.session_state:
    st.session_state.client_database = {
        "Twenty-Five Star (Pty) Ltd": {
            "trading_name": "Pedros Distribution Centre DBN",
            "reg_vat": "Co. Reg: 2022/686760/07 | VAT: 4690317583",
            "reg_address": "33 Aiken Street, Port Shepstone, KZN, 4240",
            "del_address": "4-6 Suzuka Road, Westmead, Pinetown, 3608"
        }
    }

if "sku_database" not in st.session_state:
    st.session_state.sku_database = {
        "600ml Food Flask": {
            "description": "Plain SS304 Body Configuration. Landed DDP Pinetown.",
            "default_price": 155.32
        },
        "400ml Thermal Flask": {
            "description": "Branded Pantone 176C Thermal Flask. Landed DDP Pinetown.",
            "default_price": 125.50
        },
        "YogiCup Standard": {
            "description": "Custom Molded YogiCup with Lid Specification.",
            "default_price": 45.00
        }
    }

st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>MR MOBILE SA — Commercial Document Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8;'>Enterprise Operational Engine [Locked: 2026-10-02]</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["📄 Document Generator", "📊 Enterprise Financial Tracking Dashboard"])

# ==========================================
# TAB 1: DOCUMENT GENERATOR PORTAL
# ==========================================
with tab1:
    st.subheader("Configure & Generate Commercial Document")
    
    def get_live_usd_zar_rate():
        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
            if response.status_code == 200:
                rates = response.json().get("rates", {})
                raw_rate = float(rates.get("ZAR", 18.25))
                return math.ceil(raw_rate * 100) / 100.0
        except Exception:
            pass
        return 18.25

    base_usd_zar = get_live_usd_zar_rate()

    col_a, col_b = st.columns(2)
    with col_a:
        doc_type = st.selectbox("Document Type", ["PRO FORMA TAX INVOICE", "TAX INVOICE", "QUOTATION"])
        shipping_mode = st.selectbox("Shipping Mode", ["Sea Freight", "Air Freight", "Express Courier"])
    with col_b:
        doc_date = st.date_input("Document Date", value=datetime.today())
        next_invoice_seq = len(st.session_state.invoices_db) + 1
        date_str = doc_date.strftime("%Y-%m-%d").replace("-", "")
        dynamic_doc_num = f"PI-{date_str}-{next_invoice_seq:02d}"
        doc_num = st.text_input("Document Number", value=dynamic_doc_num, disabled=True)

    col_c, col_d = st.columns(2)
    with col_c:
        due_date = st.text_input("Due Date", value="Immediate (Upon Receipt)")
    with col_d:
        validity = st.selectbox("Validity", ["1 day", "7 days", "15 days", "30 days"], index=3)

    st.markdown("---")
    st.markdown(
        f"<div style='padding: 12px; background-color: #1E293B; border-left: 4px solid #38BDF8; border-radius: 6px; color: #F8FAFC;'>"
        f"<b>Live Market FX (US$/ZAR):</b> <span style='color: #38BDF8; font-size: 16px;'><b>R {base_usd_zar:,.2f}</b></span>"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    col_cl_head1, col_cl_head2 = st.columns([3, 1])
    with col_cl_head1:
        st.markdown("### Client & Billing Details")
    with col_cl_head2:
        add_new_client_toggle = st.checkbox("➕ Add New Client")

    if add_new_client_toggle:
        client_name = st.text_input("New Client Name", value="")
        trading_name = st.text_input("Trading Name", value="")
        reg_vat = st.text_input("Co. Reg & VAT", value="")
        reg_address = st.text_input("Reg Address", value="")
        del_address = st.text_input("Delivery Address", value="")
        
        if client_name and client_name not in st.session_state.client_database:
            st.session_state.client_database[client_name] = {
                "trading_name": trading_name,
                "reg_vat": reg_vat,
                "reg_address": reg_address,
                "del_address": del_address
            }
    else:
        existing_clients = list(st.session_state.client_database.keys())
        client_name = st.selectbox("Select Existing Client", existing_clients)
        client_info = st.session_state.client_database[client_name]
        
        col_e, col_f = st.columns(2)
        with col_e:
            st.text_input("Client Name", value=client_name, disabled=True)
            trading_name = st.text_input("Trading Name", value=client_info["trading_name"])
            reg_vat = st.text_input("Co. Reg & VAT", value=client_info["reg_vat"])
        with col_f:
            reg_address = st.text_input("Reg Address", value=client_info["reg_address"])
            del_address = st.text_input("Delivery Address", value=client_info["del_address"])

    st.markdown("### Commercial Line-Item Specification")
    num_items = st.number_input("How many line items?", min_value=1, max_value=10, value=1)

    products = []
    grand_excl = 0.0
    grand_incl = 0.0

    existing_skus = list(st.session_state.sku_database.keys()) + ["+ Add New Custom SKU"]

    for i in range(int(num_items)):
        st.markdown(f"#### Item #{i+1}")
        selected_sku_option = st.selectbox(f"Select SKU / Item Code #{i+1}", existing_skus, key=f"sku_select_{i}")
        
        if selected_sku_option == "+ Add New Custom SKU":
            sku = st.text_input(f"New SKU Code #{i+1}", key=f"new_sku_{i}")
            desc = st.text_area(f"Bespoke Description #{i+1}", key=f"new_desc_{i}")
            default_p = 100.00
        else:
            sku = selected_sku_option
            sku_info = st.session_state.sku_database[sku]
            desc = st.text_area(f"Bespoke Description #{i+1}", value=sku_info["description"], key=f"desc_{i}")
            default_p = sku_info["default_price"]

        qty = st.number_input(f"Quantity (Units) #{i+1}", min_value=1, value=3000, key=f"qty_{i}")
        unit_price = st.number_input(f"Unit Price Excl. VAT (R) #{i+1}", min_value=0.0, value=float(default_p), format="%.2f", key=f"price_{i}")
        
        net_subtotal = qty * unit_price
        total_incl = net_subtotal * 1.15
        
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

    invoice_data = {
        "document_type": doc_type,
        "shipping_mode": shipping_mode,
        "invoice_date": doc_date,
        "invoice_num": dynamic_doc_num,
        "due_date": due_date,
        "validity": validity,
        "exchange_rate_display": f"R {base_usd_zar:,.2f}",
        "supplier_details": SUPPLIER_DETAILS,
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

    if st.button("Generate PDF Invoice", type="primary"):
        try:
            pdf_buffer = build_pdf_document(invoice_data)
            pdf_bytes = pdf_buffer.getvalue()
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

            # Direct Download HTML Injection (Bypasses iOS PDF preview screen)
            download_html = f"""
                <div style="margin-top: 15px; text-align: center;">
                    <a id="auto_pdf_dl" href="data:application/pdf;base64,{b64_pdf}" download="{dynamic_doc_num}.pdf" style="
                        display: inline-block;
                        padding: 14px 28px;
                        background-color: #0284C7;
                        color: #FFFFFF;
                        font-weight: bold;
                        font-size: 16px;
                        text-decoration: none;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                    ">
                        📥 Download {dynamic_doc_num}.pdf Directly to Device
                    </a>
                </div>
            """
            
            st.success("PDF generated successfully!")
            st.markdown(download_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error generating PDF: {e}")

# ==========================================
# TAB 2: INVOICE TRACKING DASHBOARD
# ==========================================
with tab2:
    st.subheader("Enterprise Financial Tracking Dashboard")
    if not st.session_state.invoices_db:
        st.info("No invoices generated yet.")
    else:
        df_invoices = pd.DataFrame(st.session_state.invoices_db)
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Billed Portfolio", f"R {df_invoices['invoice_total'].sum():,.2f}")
        col_m2.metric("Total Collected", f"R {df_invoices['amount_paid'].sum():,.2f}")
        col_m3.metric("Total Outstanding Balance", f"R {df_invoices['balance_outstanding'].sum():,.2f}")

        st.markdown("---")
        display_df = pd.DataFrame(st.session_state.invoices_db)
        display_df.columns = ["Invoice No", "Client Name", "Trading Name", "Total (R)", "Deposit (R)", "Status", "Paid (R)", "Outstanding (R)", "Date"]
        st.dataframe(display_df, use_container_width=True)
