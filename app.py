# ==============================================================================
# SCRIPT MODULE : app.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 11:45:00 SAST
# LOCKED BY     : Nisaar Ally
# STATUS        : PRODUCTION LOCKED (SARS-Compliant Engine)
# ==============================================================================

import streamlit as st
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import date

import config
from pdf_engine import generate_sars_pdf

# Page Configuration
st.set_page_config(page_title="Mr Mobile SA - Document Engine", page_icon="📱", layout="wide")

st.title("📱 Mr Mobile SA — Enterprise Document & Dispatch Engine")

# Self-Healing Session Guard
def initialize_and_repair_session():
    """Verifies session state integrity and auto-repairs corrupted structures."""
    default_item = {"desc": "600ml Food Flask (Plain SS304 Body Configuration)", "qty": 3000, "price": 155.32}
    
    if "items" not in st.session_state or not isinstance(st.session_state.items, list):
        st.session_state.items = [default_item]
    else:
        # Validate that every element inside list is a valid dict
        repaired_items = []
        for item in st.session_state.items:
            if isinstance(item, dict) and "desc" in item and "qty" in item and "price" in item:
                repaired_items.append(item)
            else:
                repaired_items.append(default_item)
        st.session_state.items = repaired_items if repaired_items else [default_item]

initialize_and_repair_session()

# Sidebar Control
st.sidebar.markdown("### 🔒 System Audit & Controls")
st.sidebar.success("""
**Status:** Operational / Flawless Lock  
**Author:** Nisaar Ally  
**Timestamp:** 2026-10-04 11:45:00 SAST  
**Auto-Backup:** Daily at 23:45 SAST  
**Sender:** fantastic1za@gmail.com  
""")

if st.sidebar.button("🔄 Reset / Clear Session Memory"):
    st.session_state.clear()
    initialize_and_repair_session()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Document Parameters")
doc_type = st.sidebar.selectbox("Document Type", ["TAX INVOICE", "PRO FORMA TAX INVOICE", "QUOTATION"])
doc_ref = st.sidebar.text_input("Reference Number", value="PI-20261002-02")
doc_date = st.sidebar.date_input("Document Date", value=date.today())

st.sidebar.markdown("---")
st.sidebar.header("Client Parameters")
client_name = st.sidebar.text_input("Client Name", value="Twenty-Five Star (Pty) Ltd")
client_vat = st.sidebar.text_input("Client VAT Registration", value="4690317583")
client_email = st.sidebar.text_input("Client Email Address", value="nisaar@fantastic1.com")

# Main Interface Tabs
tab1, tab2 = st.tabs(["📄 Document & Email Dispatch Engine", "📊 System Banking & SWIFT Ledger"])

with tab1:
    st.subheader(f"Line Items Specification — {doc_type}")
    
    # Safe Iteration
    for idx, item in enumerate(st.session_state.items):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            item["desc"] = st.text_input(f"Description #{idx+1}", value=str(item.get("desc", "")), key=f"desc_{idx}")
        with col2:
            try:
                curr_qty = int(item.get("qty", 1))
            except (ValueError, TypeError):
                curr_qty = 1
            item["qty"] = st.number_input(f"Qty #{idx+1}", min_value=1, value=curr_qty, key=f"qty_{idx}")
        with col3:
            try:
                curr_price = float(item.get("price", 0.0))
            except (ValueError, TypeError):
                curr_price = 0.0
            item["price"] = st.number_input(f"Unit Price (Excl) #{idx+1}", min_value=0.0, value=curr_price, step=10.0, key=f"price_{idx}")

    col_add, col_rem = st.columns([1, 1])
    with col_add:
        if st.button("➕ Add Line Item"):
            st.session_state.items.append({"desc": "", "qty": 1, "price": 0.0})
            st.rerun()
    with col_rem:
        if len(st.session_state.items) > 1:
            if st.button("➖ Remove Line Item"):
                st.session_state.items.pop()
                st.rerun()

    st.markdown("---")
    
    # Financial Totals Calculation
    subtotal = sum(float(i.get("qty", 1)) * float(i.get("price", 0.0)) for i in st.session_state.items)
    vat = subtotal * config.TAX_RATE
    grand_total = subtotal + vat
    deposit = grand_total * 0.50

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Subtotal (Excl)", f"R {subtotal:,.2f}")
    c2.metric("VAT (15%)", f"R {vat:,.2f}")
    c3.metric("Grand Total (Incl)", f"R {grand_total:,.2f}")
    c4.metric("50% Tranche Deposit", f"R {deposit:,.2f}")

    st.markdown("---")

    # Document Payload
    invoice_payload = {
        "doc_type": doc_type,
        "invoice_number": doc_ref,
        "date": str(doc_date),
        "client_name": client_name,
        "client_vat": client_vat,
        "client_email": client_email,
        "items": st.session_state.items
    }

    pdf_bytes = generate_sars_pdf(invoice_payload)

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        st.download_button(
            label="⬇️ Download PDF Document",
            data=pdf_bytes,
            file_name=f"{doc_ref}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Client Email Dispatch Section
    st.markdown("### 📧 Direct Client Email Dispatch")
    st.info(f"Target Recipient Address: **{client_email}**")
    
    email_confirmed = st.checkbox(f"I confirm that '{client_email}' is the correct and verified client email address.")

    if st.button("🚀 Send Email to Client", type="primary", use_container_width=True):
        if not email_confirmed:
            st.error("⚠️️ Please check the confirmation box above to verify the recipient email address before sending.")
        elif not client_email or "@" not in client_email:
            st.error("⚠️ Invalid recipient email address specified.")
        else:
            with st.spinner("Connecting to Gmail SMTP relay (with fallback redundancy) and dispatching document..."):
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
                        
                        <p>Thank you for your valued business and continued support. Please find attached your official SARS-compliant <b>{doc_type}</b> for immediate review.</p>
                        
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
                        
                        <p>Please refer to the attached PDF document for itemized breakdowns, production milestone terms, and corporate FNB banking parameters.</p>
                        
                        <p>Should you require any further assistance or clarification, please contact me directly using the links below:</p>
                        
                        <hr style="border: 0; border-top: 1px solid #dddddd; margin: 20px 0;">
                        
                        <p><b>Regards,</b><br/>
                        <strong>Nisaar Ally</strong><br/>
                        📱 Mobile: <a href="tel:+27687274731" style="color: #0066cc; text-decoration: none;">068 727 4731</a> 📲<br/>
                        📱 Secondary: <a href="tel:+27687101939" style="color: #0066cc; text-decoration: none;">068 710 1939</a> 📲<br/>
                        💬 WhatsApp: <a href="https://wa.me/27827867712" style="color: #25D366; text-decoration: none; font-weight: bold;">082 786 7712</a><br/>
                        📧 Email: <a href="mailto:nisaar@fantastic1.com" style="color: #0066cc; text-decoration: none;">nisaar@fantastic1.com</a> 📧
                        </p>
                    </body>
                    </html>
                    """
                    
                    msg.attach(MIMEText(html_body, 'html'))

                    attachment = MIMEApplication(pdf_bytes, Name=f"{doc_ref}.pdf")
                    attachment['Content-Disposition'] = f'attachment; filename="{doc_ref}.pdf"'
                    msg.attach(attachment)

                    # Redundant SMTP Dispatch (Primary SSL Port 465 -> Fallback STARTTLS Port 587)
                    sent_successfully = False
                    try:
                        server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PRIMARY_PORT, timeout=10)
                        server.login(config.SMTP_SENDER, config.SMTP_PASSWORD)
                        server.sendmail(config.SMTP_SENDER, client_email, msg.as_string())
                        server.quit()
                        sent_successfully = True
                    except Exception as primary_error:
                        # Fallback to Port 587 STARTTLS if SSL Port 465 fails
                        try:
                            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_FALLBACK_PORT, timeout=10)
                            server.starttls()
                            server.login(config.SMTP_SENDER, config.SMTP_PASSWORD)
                            server.sendmail(config.SMTP_SENDER, client_email, msg.as_string())
                            server.quit()
                            sent_successfully = True
                        except Exception as fallback_error:
                            raise Exception(f"Primary SSL Error: {str(primary_error)} | Fallback STARTTLS Error: {str(fallback_error)}")

                    if sent_successfully:
                        st.success(f"✅ Success! {doc_type} successfully emailed to **{client_email}**.")

                except Exception as e:
                    st.error(f"❌ Failed to send email: {str(e)}")

with tab2:
    st.subheader("System Banking & SWIFT Configurations")
    st.json(config.BANKING_DETAILS)
