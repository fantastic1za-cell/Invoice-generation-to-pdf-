# ==============================================================================
# SCRIPT MODULE : app.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 16:10:00 SAST
# LOCKED BY     : Nisaar Ally
# STATUS        : PRODUCTION LOCKED (In-App PDF Viewer + Native Mobile Controls)
# ==============================================================================

import streamlit as st
import smtplib
import pandas as pd
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import date

import config
from pdf_engine import generate_sars_pdf

# Page Configuration
st.set_page_config(page_title="Mr Mobile SA - Enterprise Document Engine", page_icon="📱", layout="wide")

# POP STORAGE DIRECTORY INITIALIZATION
POP_STORAGE_DIR = "uploaded_pops"
os.makedirs(POP_STORAGE_DIR, exist_ok=True)

# AUTOMATED PRODUCTION-GRADE SESSION SANITIZER
def auto_sanitize_session_state():
    """Validates and enforces strict data types and compliance default states on boot."""
    
    default_item = {
        "desc": "600ml Food Flask\nPlain SS304 Body Configuration. Landed DDP Pinetown.",
        "qty": 3000,
        "price": 155.32
    }
    if "invoice_items" not in st.session_state or not isinstance(st.session_state.invoice_items, list):
        st.session_state.invoice_items = [default_item]
    else:
        valid_items = [
            i for i in st.session_state.invoice_items 
            if isinstance(i, dict) and "desc" in i and "qty" in i and "price" in i
        ]
        st.session_state.invoice_items = valid_items if valid_items else [default_item]

    default_db = {
        "Twenty-Five Star (Pty) Ltd": {
            "trading": "Pedros Distribution Centre DBN",
            "vat": "Co. Reg: 2022/686760/07 | VAT: 4690317583",
            "reg_address": "33 Aiken Street, Port Shepstone, KZN, 4240",
            "delivery_address": "4-6 Suzuka Road, Westmead, Pinetown, 3608",
            "email": "nisaar@fantastic1.com"
        },
        "Phatbuns SA": {
            "trading": "Phatbuns Retail South Africa",
            "vat": "Co. Reg: 2021/889102/07 | VAT: 4982103982",
            "reg_address": "Clearwater Mall, Roodepoort, GP",
            "delivery_address": "Shop 14, Clearwater Mall, Roodepoort",
            "email": "info@phatbuns.co.za"
        }
    }
    if "client_database" not in st.session_state or not isinstance(st.session_state.client_database, dict):
        st.session_state.client_database = default_db

    if "processed_ledger" not in st.session_state or not isinstance(st.session_state.processed_ledger, list):
        st.session_state.processed_ledger = [
            {
                "Ref": "PI-20261002-01",
                "Client": "Twenty-Five Star (Pty) Ltd",
                "Type": "PRO FORMA TAX INVOICE",
                "Subtotal": 465960.00,
                "VAT": 69894.00,
                "Total": 535854.00,
                "50% Tranche": 267927.00,
                "Status": "Awaiting POP / Deposit",
                "POP File Path": None
            }
        ]

    if "show_add_client_form" not in st.session_state:
        st.session_state.show_add_client_form = False

    if "show_in_app_preview" not in st.session_state:
        st.session_state.show_in_app_preview = False

auto_sanitize_session_state()

# App Header & System Info
st.title("📱 Mr Mobile SA — Enterprise Document & Financial Engine")
st.caption("Operational Engine | SARS VAT Compliant [Locked: 2026-10-04]")

st.sidebar.markdown("### 🔒 System Audit & Status")
st.sidebar.success("""
**Status:** Operational (Auto-Guarded)  
**Author:** Nisaar Ally  
**Timestamp:** 2026-10-04 16:10:00 SAST  
**Auto-Backup:** Active (Daily 23:45 SAST)  
**Sender:** fantastic1za@gmail.com  
""")

# Main Navigation Tabs
tab1, tab2 = st.tabs([
    "📄 Commercial Document Generator", 
    "📊 Financial Tracking Dashboard & POP Verification"
])

# ------------------------------------------------------------------------------
# TAB 1: DOCUMENT GENERATOR & CLIENT CAPTURE
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Configure Commercial Document")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        doc_type = st.selectbox("Document Type", ["PRO FORMA TAX INVOICE", "TAX INVOICE", "QUOTATION"])
    with col_d2:
        shipping_mode = st.selectbox("Shipping Mode", ["Sea Freight", "Air Freight", "Local Express"])
    with col_d3:
        doc_date = st.date_input("Document Date", value=date.today())

    doc_ref = st.text_input("Document Number / Ref", value="PI-20261002-02")

    st.markdown("---")
    st.subheader("Client Selection & Client Capture")

    client_list = list(st.session_state.client_database.keys())
    
    col_select, col_add_btn = st.columns([3, 1])
    with col_select:
        selected_client_name = st.selectbox("Select Existing Client", client_list)
    with col_add_btn:
        st.write("")
        st.write("")
        if st.button("➕ Add New Client"):
            st.session_state.show_add_client_form = not st.session_state.show_add_client_form

    if st.session_state.show_add_client_form:
        st.info("💡 Capturing New Client Parameters:")
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            new_client_name = st.text_input("New Client Name")
            new_client_trading = st.text_input("Trading Name")
            new_client_vat = st.text_input("Reg & VAT Details")
        with c_col2:
            new_client_reg_addr = st.text_input("Registered Address")
            new_client_del_addr = st.text_input("Delivery Address")
            new_client_email = st.text_input("Client Email Address")

        if st.button("💾 Save New Client"):
            if not new_client_name:
                st.error("⚠️ Client name is required.")
            elif not new_client_email or "@" not in new_client_email:
                st.error("⚠️ Valid email address is required.")
            else:
                st.session_state.client_database[new_client_name] = {
                    "trading": new_client_trading,
                    "vat": new_client_vat,
                    "reg_address": new_client_reg_addr,
                    "delivery_address": new_client_del_addr,
                    "email": new_client_email
                }
                st.session_state.show_add_client_form = False
                st.success(f"Client '{new_client_name}' successfully saved!")
                st.rerun()

    # Load Client Details
    client_info = st.session_state.client_database.get(selected_client_name, {})
    client_name = selected_client_name
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        client_trading = st.text_input("Trading Name", value=client_info.get("trading", ""))
        client_vat = st.text_input("Co. Reg & VAT Details", value=client_info.get("vat", ""))
        reg_address = st.text_input("Registered Address", value=client_info.get("reg_address", ""))
    with c_col2:
        delivery_address = st.text_input("Delivery Address", value=client_info.get("delivery_address", ""))
        client_email = st.text_input("Client Email Address", value=client_info.get("email", ""))

    if client_name in st.session_state.client_database:
        st.session_state.client_database[client_name]["trading"] = client_trading
        st.session_state.client_database[client_name]["vat"] = client_vat
        st.session_state.client_database[client_name]["reg_address"] = reg_address
        st.session_state.client_database[client_name]["delivery_address"] = delivery_address
        st.session_state.client_database[client_name]["email"] = client_email

    st.markdown("---")
    st.subheader(f"Line Items Specification — {doc_type}")

    for idx, item in enumerate(st.session_state.invoice_items):
        item["desc"] = st.text_area(f"Description #{idx+1}", value=str(item.get("desc", "")), key=f"desc_{idx}", height=68)
        col_q, col_p = st.columns(2)
        with col_q:
            item["qty"] = st.number_input(f"Qty #{idx+1}", min_value=1, value=int(item.get("qty", 1)), key=f"qty_{idx}")
        with col_p:
            item["price"] = st.number_input(f"Unit Price (Excl) #{idx+1}", min_value=0.0, value=float(item.get("price", 0.0)), step=10.0, key=f"price_{idx}")

    col_add, col_rem = st.columns([1, 1])
    with col_add:
        if st.button("➕ Add Line Item"):
            st.session_state.invoice_items.append({"desc": "", "qty": 1, "price": 0.0})
            st.rerun()
    with col_rem:
        if len(st.session_state.invoice_items) > 1:
            if st.button("➖ Remove Line Item"):
                st.session_state.invoice_items.pop()
                st.rerun()

    st.markdown("---")

    # Financial Calculations
    subtotal = sum(float(i.get("qty", 1)) * float(i.get("price", 0.0)) for i in st.session_state.invoice_items)
    vat = subtotal * config.TAX_RATE
    grand_total = subtotal + vat
    deposit = grand_total * 0.50

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Subtotal (Excl)", f"R {subtotal:,.2f}")
    c2.metric("VAT (15%)", f"R {vat:,.2f}")
    c3.metric("Grand Total (Incl)", f"R {grand_total:,.2f}")
    c4.metric("50% Tranche Deposit", f"R {deposit:,.2f}")

    st.markdown("---")

    # PDF Payload Generation
    invoice_payload = {
        "doc_type": doc_type,
        "invoice_number": doc_ref,
        "date": str(doc_date),
        "shipping_mode": shipping_mode,
        "client_name": client_name,
        "client_trading": client_trading,
        "client_vat": client_vat,
        "reg_address": reg_address,
        "delivery_address": delivery_address,
        "client_email": client_email,
        "items": st.session_state.invoice_items
    }

    pdf_bytes = generate_sars_pdf(invoice_payload)

    # Dispatch Controls
    st.markdown("### 🚀 Document Output & Dispatch")
    
    col_prev, col_dl, col_em = st.columns(3)

    with col_prev:
        if st.button("👁️ Preview PDF In-App", use_container_width=True):
            st.session_state.show_in_app_preview = not st.session_state.show_in_app_preview

    with col_dl:
        st.download_button(
            label="⬇️ Download PDF File",
            data=pdf_bytes,
            file_name=f"{doc_ref}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col_em:
        if st.button("📧 Dispatch via Email", type="primary", use_container_width=True):
            if not client_email or "@" not in client_email:
                st.error("❌ Email address missing or invalid.")
            else:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"Nisaar Ally <{config.SMTP_SENDER}>"
                    msg['To'] = client_email
                    msg['Subject'] = f"{doc_type} Ref: {doc_ref}"

                    html_body = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #222222; line-height: 1.6;">
                        <h2 style="color: #0f1d2f;">{doc_type} — Ref: {doc_ref}</h2>
                        <p>Dear {client_name},</p>
                        <p>Please find attached your official SARS-compliant <b>{doc_type}</b>.</p>
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #0f1d2f; margin: 15px 0;">
                            <h4 style="margin-top: 0;">Summary of Account:</h4>
                            <ul>
                                <li><b>Reference Number:</b> {doc_ref}</li>
                                <li><b>Subtotal (Excl. VAT):</b> R {subtotal:,.2f}</li>
                                <li><b>VAT (15%):</b> R {vat:,.2f}</li>
                                <li><b>Grand Total (Incl. VAT):</b> R {grand_total:,.2f}</li>
                                <li><b>50% Required Tranche Deposit:</b> R {deposit:,.2f}</li>
                            </ul>
                        </div>
                        <p>Please email proof of payment to initiate manufacturing.</p>
                        <hr style="border: 0; border-top: 1px solid #dddddd; margin: 20px 0;">
                        <p><b>Regards,</b><br/>
                        <strong>Nisaar Ally</strong><br/>
                        📱 Mobile: 068 727 4731 / 068 710 1939<br/>
                        💬 WhatsApp: 082 786 7712<br/>
                        📧 Email: nisaar@fantastic1.com
                        </p>
                    </body>
                    </html>
                    """

                    msg.attach(MIMEText(html_body, 'html'))
                    attachment = MIMEApplication(pdf_bytes, Name=f"{doc_ref}.pdf")
                    attachment['Content-Disposition'] = f'attachment; filename="{doc_ref}.pdf"'
                    msg.attach(attachment)

                    server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
                    server.login(config.SMTP_SENDER, config.SMTP_PASSWORD)
                    server.sendmail(config.SMTP_SENDER, client_email, msg.as_string())
                    server.quit()

                    already_exists = any(item.get("Ref") == doc_ref for item in st.session_state.processed_ledger)
                    if not already_exists:
                        new_entry = {
                            "Ref": doc_ref,
                            "Client": client_name,
                            "Type": doc_type,
                            "Subtotal": subtotal,
                            "VAT": vat,
                            "Total": grand_total,
                            "50% Tranche": deposit,
                            "Status": "Awaiting POP / Deposit",
                            "POP File Path": None
                        }
                        st.session_state.processed_ledger.append(new_entry)

                    st.success(f"✅ Document successfully dispatched to {client_email} and recorded in ledger!")
                
                except Exception as e:
                    st.error(f"❌ Failed to dispatch email: {str(e)}")

    # In-App PDF Viewer Render
    if st.session_state.show_in_app_preview:
        st.markdown("---")
        st.markdown("### 👁️ In-App PDF Document Viewer")
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="650" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: FINANCIAL TRACKING DASHBOARD & POP VERIFICATION
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("📊 Financial Tracking & Ledger Operations")

    df_ledger = pd.DataFrame(st.session_state.processed_ledger)

    total_processed = df_ledger["Total"].sum()
    received_deposits = df_ledger[df_ledger["Status"] == "Deposit Received"]["50% Tranche"].sum()
    pending_deposits = df_ledger[df_ledger["Status"] != "Deposit Received"]["50% Tranche"].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Processed Volume", f"R {total_processed:,.2f}")
    m2.metric("Deposits Confirmed (Received)", f"R {received_deposits:,.2f}")
    m3.metric("Outstanding Deposits Pending", f"R {pending_deposits:,.2f}")

    st.markdown("---")
    st.subheader("Commercial Transactions Ledger")
    st.dataframe(df_ledger, use_container_width=True)

    st.markdown("---")
    st.subheader("📌 Upload Proof of Payment (POP) & Verify Deposit")

    pending_refs = [item["Ref"] for item in st.session_state.processed_ledger]
    
    if pending_refs:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            selected_ref = st.selectbox("Select Invoice Reference", pending_refs)
            pop_file = st.file_uploader("Upload Proof of Payment (PDF / JPG / PNG)", type=["pdf", "jpg", "jpeg", "png"])
        
        with col_p2:
            st.write("")
            st.write("")
            current_item = next((item for item in st.session_state.processed_ledger if item["Ref"] == selected_ref), None)
            if current_item:
                st.info(f"**Selected Ref:** {current_item['Ref']}\n\n"
                        f"**Client:** {current_item['Client']}\n\n"
                        f"**Required Deposit:** R {current_item['50% Tranche']:,.2f}\n\n"
                        f"**Current Status:** `{current_item['Status']}`\n\n"
                        f"**Stored POP Path:** `{current_item.get('POP File Path', 'None')}`")

                if st.button("✅ Upload POP & Confirm Deposit Received", type="primary", use_container_width=True):
                    if pop_file is None and current_item.get("POP File Path") is None:
                        st.error("⚠️ Please attach a valid PDF, JPG, or PNG Proof of Payment file.")
                    else:
                        if pop_file is not None:
                            file_ext = pop_file.name.split(".")[-1]
                            saved_filename = f"POP_{selected_ref}_{date.today().strftime('%Y%m%d')}.{file_ext}"
                            saved_filepath = os.path.join(POP_STORAGE_DIR, saved_filename)

                            with open(saved_filepath, "wb") as f:
                                f.write(pop_file.getbuffer())

                            current_item["POP File Path"] = saved_filepath

                        current_item["Status"] = "Deposit Received"
                        st.success(f"POP uploaded successfully and stored at `{current_item['POP File Path']}`! Status set to 'Deposit Received'.")
                        st.rerun()

                if current_item.get("POP File Path") and os.path.exists(current_item["POP File Path"]):
                    st.markdown("---")
                    st.markdown("### 👁️ Stored Proof of Payment Document")
                    file_path = current_item["POP File Path"]
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        st.image(file_path, caption=f"Stored POP: {os.path.basename(file_path)}")
                    elif file_path.lower().endswith('.pdf'):
                        with open(file_path, "rb") as f:
                            pdf_data = f.read()
                        st.download_button(
                            label=f"📥 Download Stored POP PDF ({os.path.basename(file_path)})",
                            data=pdf_data,
                            file_name=os.path.basename(file_path),
                            mime="application/pdf"
                        )
    else:
        st.info("No active transactions available for verification.")
