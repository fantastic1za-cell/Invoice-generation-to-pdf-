# ==============================================================================
# SCRIPT MODULE : app.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 12:10:00 SAST
# LOCKED BY     : Nisaar Ally
# STATUS        : PRODUCTION LOCKED (SARS-Compliant Engine)
# ==============================================================================

import streamlit as st
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import date

import config
from pdf_engine import generate_sars_pdf

# Page Config
st.set_page_config(page_title="Mr Mobile SA - Enterprise Document Engine", page_icon="📱", layout="wide")

st.title("📱 Mr Mobile SA — Enterprise Document & Financial Engine")
st.caption("Operational Engine [Locked: 2026-10-04]")

# Defensively Initialize Session Memory Structures
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = [{"desc": "600ml Food Flask (Plain SS304 Body Configuration)", "qty": 3000, "price": 155.32}]

if "client_database" not in st.session_state:
    st.session_state.client_database = {
        "Twenty-Five Star (Pty) Ltd": {"vat": "4690317583", "email": "nisaar@fantastic1.com"},
        "Phatbuns SA": {"vat": "4982103982", "email": "info@phatbuns.co.za"},
        "Doorstep Desserts": {"vat": "4120938491", "email": "accounts@doorstepdesserts.co.za"}
    }

if "processed_ledger" not in st.session_state:
    st.session_state.processed_ledger = [
        {"Ref": "PI-20261002-01", "Client": "Twenty-Five Star (Pty) Ltd", "Type": "PRO FORMA TAX INVOICE", "Subtotal": 465960.00, "VAT": 69894.00, "Total": 535854.00, "50% Tranche": 267927.00, "Status": "Deposit Received"},
        {"Ref": "INV-20260928-04", "Client": "Phatbuns SA", "Type": "TAX INVOICE", "Subtotal": 120000.00, "VAT": 18000.00, "Total": 138000.00, "50% Tranche": 69000.00, "Status": "Fully Settled"},
        {"Ref": "QUO-20260915-02", "Client": "Doorstep Desserts", "Type": "QUOTATION", "Subtotal": 85000.00, "VAT": 12750.00, "Total": 97750.00, "50% Tranche": 48875.00, "Status": "Awaiting Deposit"}
    ]

if "show_add_client_form" not in st.session_state:
    st.session_state.show_add_client_form = False

# Sidebar Controls
st.sidebar.markdown("### 🔒 System Audit & Controls")
st.sidebar.success("""
**Status:** Operational  
**Author:** Nisaar Ally  
**Timestamp:** 2026-10-04 12:10:00 SAST  
**Auto-Backup:** Active (Daily 23:45 SAST)  
**Sender:** fantastic1za@gmail.com  
""")

if st.sidebar.button("🔄 Clear App Cache & Reset Session Memory"):
    st.session_state.clear()
    st.rerun()

# Main App Navigation
tab1, tab2 = st.tabs(["📄 Commercial Document Generator", "📊 Financial Tracking Dashboard & Outstanding Balance Ledger"])

# ------------------------------------------------------------------------------
# TAB 1: DOCUMENT GENERATOR & CLIENT CAPTURE
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Configure Commercial Document")

    # Document Header Fields
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

    # Clean Dropdown: Displays ONLY captured existing clients
    client_list = list(st.session_state.client_database.keys())
    
    col_select, col_add_btn = st.columns([3, 1])
    with col_select:
        selected_client_name = st.selectbox("Select Existing Client", client_list)
    with col_add_btn:
        st.write("") # Alignment spacing
        st.write("")
        if st.button("➕ Add New Client"):
            st.session_state.show_add_client_form = not st.session_state.show_add_client_form

    # New Client Input Form
    if st.session_state.show_add_client_form:
        st.info("💡 Capturing New Client Parameters:")
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1:
            new_client_name = st.text_input("New Client Name")
        with c_col2:
            new_client_vat = st.text_input("New Client VAT / Reg Number")
        with c_col3:
            new_client_email = st.text_input("New Client Email Address")

        if st.button("💾 Save New Client"):
            if not new_client_name:
                st.error("⚠️ Client name is required.")
            elif not new_client_email or "@" not in new_client_email:
                st.error("⚠️ Valid email address is required.")
            else:
                st.session_state.client_database[new_client_name] = {"vat": new_client_vat, "email": new_client_email}
                st.session_state.show_add_client_form = False
                st.success(f"Client '{new_client_name}' successfully saved!")
                st.rerun()

    # Client Details Fields
    client_info = st.session_state.client_database.get(selected_client_name, {})
    client_name = selected_client_name
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        client_vat = st.text_input("Client VAT / Reg Number", value=client_info.get("vat", ""))
    with c_col2:
        client_email = st.text_input("Client Email Address", value=client_info.get("email", ""))
        
    # Update active dictionary if modified inline
    if client_name in st.session_state.client_database:
        st.session_state.client_database[client_name]["vat"] = client_vat
        st.session_state.client_database[client_name]["email"] = client_email

    st.markdown("---")
    st.subheader(f"Line Items Specification — {doc_type}")

    # Line Items Generator
    for idx, item in enumerate(st.session_state.invoice_items):
        item["desc"] = st.text_input(f"Description #{idx+1}", value=str(item.get("desc", "")), key=f"desc_{idx}")
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

    # Financial Totals
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

    # PDF Payload
    invoice_payload = {
        "doc_type": doc_type,
        "invoice_number": doc_ref,
        "date": str(doc_date),
        "client_name": client_name,
        "client_vat": client_vat,
        "client_email": client_email,
        "items": st.session_state.invoice_items
    }

    pdf_bytes = generate_sars_pdf(invoice_payload)

    # Unified Action Engine: Auto Email + Auto Download + Auto Tracking Record
    st.markdown("### 🚀 Dispatch & Download Engine")
    
    if not client_email or "@" not in client_email:
        st.warning("⚠️ Please provide a valid client email address above before downloading/dispatching.")
    
    col_dl, col_confirm = st.columns([2, 1])
    with col_confirm:
        email_confirmed = st.checkbox(f"Verify dispatch to: {client_email}", value=True)

    with col_dl:
        # Download button triggers local file saving
        download_clicked = st.download_button(
            label="⬇️ Download & Email PDF Document to Client",
            data=pdf_bytes,
            file_name=f"{doc_ref}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # On download action, execute email relay + ledger recording automatically
        if download_clicked:
            if email_confirmed and client_email and "@" in client_email:
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
                        
                        <p>Thank you for your business. Please find attached your official SARS-compliant <b>{doc_type}</b>.</p>
                        
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
                        
                        <p>Please refer to the attached PDF for banking and payment terms.</p>
                        
                        <hr style="border: 0; border-top: 1px solid #dddddd; margin: 20px 0;">
                        
                        <p><b>Regards,</b><br/>
                        <strong>Nisaar Ally</strong><br/>
                        📱 Mobile: <a href="tel:+27687274731">068 727 4731</a> 📲<br/>
                        📱 Secondary: <a href="tel:+27687101939">068 710 1939</a> 📲<br/>
                        💬 WhatsApp: <a href="https://wa.me/27827867712">082 786 7712</a><br/>
                        📧 Email: <a href="mailto:nisaar@fantastic1.com">nisaar@fantastic1.com</a> 📧
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

                    # Record transaction to tracking ledger
                    new_entry = {
                        "Ref": doc_ref,
                        "Client": client_name,
                        "Type": doc_type,
                        "Subtotal": subtotal,
                        "VAT": vat,
                        "Total": grand_total,
                        "50% Tranche": deposit,
                        "Status": "Awaiting Deposit"
                    }
                    st.session_state.processed_ledger.append(new_entry)
                    st.success(f"✅ Downloaded, emailed to {client_email}, and logged to tracking dashboard!")
                except Exception as e:
                    st.error(f"❌ Failed to dispatch email: {str(e)}")

# ------------------------------------------------------------------------------
# TAB 2: FINANCIAL TRACKING DASHBOARD & OUTSTANDING BALANCES
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("📊 Financial Tracking & Outstanding Balance Ledger")

    df_ledger = pd.DataFrame(st.session_state.processed_ledger)

    total_processed = df_ledger["Total"].sum()
    total_deposits = df_ledger["50% Tranche"].sum()
    total_outstanding = total_processed - total_deposits

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Processed Volume", f"R {total_processed:,.2f}")
    m2.metric("Total Deposit Tranches (50%)", f"R {total_deposits:,.2f}")
    m3.metric("Outstanding Balance Treasury", f"R {total_outstanding:,.2f}")

    st.markdown("---")
    st.subheader("Commercial Transactions Ledger")
    st.dataframe(df_ledger, use_container_width=True)
