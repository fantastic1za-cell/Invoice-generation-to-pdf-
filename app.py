import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from pdf_engine import build_pdf_document
from config import SUPPLIER_DETAILS, BANK_DETAILS_PRIMARY, BANK_DETAILS_SECONDARY

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Mr Mobile SA - Invoice Generator",
    page_icon="mmsalogo.png.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State Databases
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

# 2. Application Header & Branding (Clear, readable white text)
st.markdown(
    "<h1 style='text-align: center; color: #FFFFFF;'>MR MOBILE SA — Commercial Document & Invoicing Engine</h1>", 
    unsafe_allow_html=True
)
st.markdown("<p style='text-align: center; color: #94A3B8;'>Enterprise Management & Operations Dashboard</p>", unsafe_allow_html=True)
st.markdown("---")

# Multi-tab layout configuration
tab1, tab2 = st.tabs(["📄 Document Generator", "📊 Enterprise Financial Tracking Dashboard"])

# ==========================================
# TAB 1: DOCUMENT GENERATOR PORTAL
# ==========================================
with tab1:
    st.subheader("Configure & Generate Commercial Document")
    
    # Fetch live US$/ZAR rate (Base rate without markup)
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

    col_a, col_b = st.columns(2)
    with col_a:
        doc_type = st.selectbox("Document Type", ["PRO FORMA TAX INVOICE", "TAX INVOICE", "QUOTATION"])
        shipping_mode = st.selectbox("Shipping Mode", ["Sea Freight", "Air Freight", "Express Courier"])
    with col_b:
        doc_date = st.date_input("Document Date", value=datetime.today())
        doc_num = st.text_input("Document Number", value="PI-2026-1002-04")

    col_c, col_d = st.columns(2)
    with col_c:
        due_date = st.text_input("Due Date", value="Immediate (Upon Receipt)")
    with col_d:
        validity = st.text_input("Validity", value="30 Days")

    # Display Live Exchange Rate Block (Dark Theme Matching Container - No White Block)
    st.markdown("---")
    st.markdown(
        f"<div style='padding: 12px; background-color: #1E293B; border-left: 4px solid #38BDF8; border-radius: 6px; color: #F8FAFC;'>"
        f"<b>Live Market Exchange Rate (US$/ZAR):</b> <span style='color: #38BDF8; font-size: 16px;'><b>R {base_usd_zar:,.4f}</b></span>"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Client Selection Dropdown & Details Management
    st.markdown("### Client & Billing Details")
    
    existing_client_options = list(st.session_state.client_database.keys()) + ["+ Add New Client"]
    selected_client_option = st.selectbox("Select Existing Client or Add New", existing_client_options)

    if selected_client_option == "+ Add New Client":
        st.info("Enter details for the new client below. They will be saved to your client database.")
        client_name = st.text_input("Client Name", value="")
        trading_name = st.text_input("Trading Name", value="")
        reg_vat = st.text_input("Co. Reg & VAT", value="")
        reg_address = st.text_input("Reg Address", value="")
        del_address = st.text_input("Delivery Address", value="")
        
        # Save new client if name is provided
        if client_name and client_name not in st.session_state.client_database:
            st.session_state.client_database[client_name] = {
                "trading_name": trading_name,
                "reg_vat": reg_vat,
                "reg_address": reg_address,
                "del_address": del_address
            }
    else:
        client_name = selected_client_option
        client_info = st.session_state.client_database[client_name]
        
        col_e, col_f = st.columns(2)
        with col_e:
            st.text_input("Client Name", value=client_name, disabled=True)
            trading_name = st.text_input("Trading Name", value=client_info["trading_name"])
            reg_vat = st.text_input("Co. Reg & VAT", value=client_info["reg_vat"])
        with col_f:
            reg_address = st.text_input("Reg Address", value=client_info["reg_address"])
            del_address = st.text_input("Delivery Address", value=client_info["del_address"])

    # Line Items & SKU Database Selection
    st.markdown("### Commercial Line-Item Specification")
    num_items = st.number_input("How many products / line items?", min_value=1, max_value=10, value=1)

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
        
        # Save new SKUs back to database automatically
        if sku and sku not in st.session_state.sku_database and sku != "+ Add New Custom SKU":
            st.session_state.sku_database[sku] = {
                "description": desc,
                "default_price": unit_price
            }

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

    # Compile Invoice Data Payload
    invoice_data = {
        "document_type": doc_type,
        "shipping_mode": shipping_mode,
        "invoice_date": doc_date,
        "invoice_num": doc_num,
        "due_date": due_date,
        "validity": validity,
        "exchange_rate_display": f"R {base_usd_zar:,.4f}",
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
            
            # Register or update in dashboard database
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
        df_invoices = pd.DataFrame(st.session_state.invoices_db)

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
                st.markdown(f"**Calculated Balance Outstanding:** <span style='color:#F87171;'><b>R {new_balance:,.2f}</b></span>", unsafe_allow_html=True)

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

        st.session_state.invoices_db = updated_db

        st.markdown("---")
        st.markdown("### Master Ledger Summary Table")
        display_df = pd.DataFrame(st.session_state.invoices_db)
        display_df.columns = ["Invoice No", "Client Name", "Trading Name", "Total (R)", "Deposit (R)", "Status", "Paid (R)", "Outstanding (R)", "Date"]
        st.dataframe(display_df, use_container_width=True)
