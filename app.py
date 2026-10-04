# ==============================================================================
# SCRIPT MODULE : app.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 15:50:00 SAST
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

# AUTOMATED PRODUCTION-GRADE SESSION SANITIZER (Runs silently on boot)
def auto_sanitize_session_state():
    """Validates and enforces strict data types on st.session_state without manual intervention."""
    
    # 1. Sanitize Invoice Items
    default_item = {"desc": "600ml Food Flask\nPlain SS304 Body Configuration. Landed DDP Pinetown.", "qty": 3000, "price": 155.32}
    if "invoice_items" not in st.session_state or not isinstance(st.session_state.invoice_items, list):
        st.session_state.invoice_items = [default_item]
    else:
        valid_items = []
        for i in st.session_state.invoice_items:
            if isinstance(i, dict) and "desc" in i and "qty" in i and "price" in i:
                valid_items.append(i)
        st.session_state.invoice_items = valid_items if valid_items else [default_item]

    # 2. Sanitize Client Database
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

    # 3. Sanitize Processed Ledger
    if "processed_ledger" not in st.session_state or not isinstance(st.session_state.processed_ledger, list):
        st.session_state.processed_ledger = [
            {"Ref": "PI-20261002-01", "Client": "Twenty-Five Star (Pty) Ltd", "Type": "PRO FORMA TAX INVOICE", "Subtotal": 465960.00, "VAT": 69894.00, "Total": 535854.00, "50% Tranche": 267927.00, "Status": "Deposit Received"}
        ]

    # 4. Flags
    if "show_add_client_form" not in st.session_state:
        st.session_state.show_add_client_form = False
    if "dispatch_completed" not in st.session_state:
        st.session_state.dispatch_completed = False

# Execute automated state guard
auto_sanitize_session_state()

# App Header
st.title("📱 Mr Mobile SA — Enterprise Document & Financial Engine")
st.caption("Operational Engine [Locked: 2026-10-04]")

# Sidebar System Information
st.sidebar.markdown("### 🔒 System Audit & Status")
st.sidebar.success("""
**Status:** Operational (Auto-Guarded)  
**Author:** Nisaar Ally  
**Timestamp:** 2026-10-04 15:50:00 SAST  
**Auto-Backup:** Active (Daily 23:45 SAST)  
**Sender:** fantastic1za@gmail.com  
""")

# iOS Preview Return Navigation Screen
if st.session_state.dispatch_completed:
    st.success("✅ **Commercial Document Dispatched & Processed Successfully!**")
    st.info("The PDF was generated cleanly without watermarks, emailed to the client, and logged to your Financial Ledger.")
    
    if st.button("⬅️ Return to Main Application Dashboard", type="primary", use_container_width=True):
        st.session_state.dispatch_completed = False
        st.rerun()

else:
    # Main App Navigation
    tab1, tab2 = st.tabs(["📄 Commercial Document Generator", "📊 Financial Tracking Dashboard & Outstanding Balance Ledger"])

    # --------------------------------------------------------------------------
    # TAB 1: DOCUMENT GENERATOR & CLIENT CAPTURE
    # --------------------------------------------------------------------------
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

        # Clean Dropdown containing strictly captured clients
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

        # Sync changes back to active state
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

        # PDF Payload
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

        # Dispatch & Download Engine
        st.markdown("### 🚀 Dispatch & Download Engine")
        
        if not client_email or "@" not in client_email:
            st.warning("⚠️ Please provide a valid client email address above before dispatching.")
        
        col_dl, col_confirm = st.columns([2, 1])
        with col_confirm:
            email_confirmed = st.checkbox(f"Verify dispatch to: {client_email}", value=True)

        with col_dl:
            download_clicked = st.download_button(
                label="⬇️ Download & Email PDF Document to Client",
                data=pdf_bytes,
                file_name=f"{doc_ref}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

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
                        st.session_state.dispatch_completed = True
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Failed to dispatch email: {str(e)}")

    # --------------------------------------------------------------------------
    # TAB 2: FINANCIAL TRACKING DASHBOARD & OUTSTANDING BALANCES
    # --------------------------------------------------------------------------
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
