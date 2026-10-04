# ==============================================================================
# SCRIPT MODULE : app.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 12:05:00 SAST
# LOCKED BY     : Nisaar Ally
# STATUS        : PRODUCTION LOCKED (SARS-Compliant Engine)
# ==============================================================================

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import date

import config
from pdf_engine import generate_sars_pdf

# Page Config
st.set_page_config(page_title="Mr Mobile SA - Document Engine", page_icon="📱", layout="wide")

st.title("📱 Mr Mobile SA — Commercial Document Generator")
st.caption("Enterprise Operational Engine [Locked: 2026-10-04]")

# Sidebar Controls
st.sidebar.markdown("### 🔒 System Audit & Controls")
st.sidebar.success("""
**Status:** Operational  
**Author:** Nisaar Ally  
**Timestamp:** 2026-10-04 12:05:00 SAST  
**Auto-Backup:** Daily at 23:45 SAST  
**Sender:** fantastic1za@gmail.com  
""")

# Session State Initialization
if "items" not in st.session_state or not isinstance(st.session_state.items, list):
    st.session_state.items = [{"desc": "600ml Food Flask (Plain SS304 Body Configuration)", "qty": 3000, "price": 155.32}]

tab1, tab2 = st.tabs(["📄 Document Generator", "📊 Enterprise Financial Tracking Dashboard"])

with tab1:
    st.subheader("Configure & Generate Commercial Document")

    # Document Header Parameters
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        doc_type = st.selectbox("Document Type", ["PRO FORMA TAX INVOICE", "TAX INVOICE", "QUOTATION"])
    with col_d2:
        shipping_mode = st.selectbox("Shipping Mode", ["Sea Freight", "Air Freight", "Local Express"])
    with col_d3:
        doc_date = st.date_input("Document Date", value=date.today())

    doc_ref = st.text_input("Document Number / Ref", value="PI-20261002-02")

    st.markdown("---")
    st.subheader("Client & Billing Details")
    
    # Client Details Capture Fields (Restored)
    client_name = st.text_input("Client Name", value="Twenty-Five Star (Pty) Ltd")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        client_vat = st.text_input("Client VAT / Reg Number", value="4690317583")
    with col_c2:
        client_email = st.text_input("Client Email Address", value="nisaar@fantastic1.com")

    st.markdown("---")
    st.subheader(f"Line Items Specification — {doc_type}")
    
    # Line Item Rows
    for idx, item in enumerate(st.session_state.items):
        item["desc"] = st.text_input(f"Description #{idx+1}", value=str(item.get("desc", "")), key=f"desc_{idx}")
        col_q, col_p = st.columns(2)
        with col_q:
            item["qty"] = st.number_input(f"Qty #{idx+1}", min_value=1, value=int(item.get("qty", 1)), key=f"qty_{idx}")
        with col_p:
            item["price"] = st.number_input(f"Unit Price (Excl) #{idx+1}", min_value=0.0, value=float(item.get("price", 0.0)), step=10.0, key=f"price_{idx}")

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

    # Document Payload Assembly
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

    # Email Dispatch Interface with Address Confirmation
    st.markdown("### 📧 Direct Client Email Dispatch")
    st.info(f"Target Recipient Address: **{client_email}**")
    
    email_confirmed = st.checkbox(f"I confirm that '{client_email}' is the correct and verified client email address.")

    if st.button("🚀 Send Email to Client", type="primary", use_container_width=True):
        if not email_confirmed:
            st.error("⚠️ Please check the confirmation box above to verify the recipient email address before dispatching.")
        elif not client_email or "@" not in client_email:
            st.error("⚠️ Invalid recipient email address specified.")
        else:
            with st.spinner("Connecting to Gmail SMTP relay and dispatching email..."):
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
                        
                        <p>Please refer to the attached PDF for itemized breakdowns, production milestone terms, and corporate FNB banking parameters.</p>
                        
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

                    server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
                    server.login(config.SMTP_SENDER, config.SMTP_PASSWORD)
                    server.sendmail(config.SMTP_SENDER, client_email, msg.as_string())
                    server.quit()

                    st.success(f"✅ Success! {doc_type} successfully emailed to **{client_email}**.")

                except Exception as e:
                    st.error(f"❌ Failed to send email: {str(e)}")

with tab2:
    st.subheader("System Banking & Compliance Ledger")
    st.json(config.BANKING_DETAILS)
