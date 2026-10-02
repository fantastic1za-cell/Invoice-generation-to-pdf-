import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set page setup
st.set_page_config(page_title="Pro Forma Invoice Generator", page_icon="📄", layout="wide")

# Pre-stored Clients Database
PRESET_CLIENTS = {
    "Twenty-Five Star (Pty) Ltd (Pedros DBN)": {
        "client_name": "Twenty-Five Star (Pty) Ltd",
        "trading_name": "Pedros Distribution Centre DBN",
        "reg_vat": "Co. Reg: 2022/686760/07 | VAT: 4690317583",
        "reg_address": "33 Aiken Street, Port Shepstone, KZN, 4240",
        "del_address": "4-6 Suzuka Road, Westmead, Pinetown, 3608"
    }
}

st.title("📄 Pro Forma Invoice Generator")

# ---------------------------------------------------------
# 1. INVOICE HEADER
# ---------------------------------------------------------
st.header("1. General Details")
col1, col2 = st.columns(2)
with col1:
    invoice_date = st.date_input("Invoice Date", datetime.today())
with col2:
    invoice_num = st.text_input("Invoice Number", f"PI-{invoice_date.strftime('%Y%m%d')}-001")

st.markdown("---")

# ---------------------------------------------------------
# 2. CLIENT & DELIVERY DETAILS
# ---------------------------------------------------------
st.header("2. Client & Delivery Details")

client_option = st.radio("Select Client Mode:", ["Existing Client", "New Client"], horizontal=True)

if client_option == "Existing Client":
    selected_preset = st.selectbox("Choose Client Preset:", list(PRESET_CLIENTS.keys()))
    preset_data = PRESET_CLIENTS[selected_preset]
    
    client_name = st.text_input("Client Name", value=preset_data["client_name"])
    trading_name = st.text_input("Trading Name", value=preset_data["trading_name"])
    reg_vat = st.text_input("Co. Reg & VAT", value=preset_data["reg_vat"])
    reg_address = st.text_area("Registered Address", value=preset_data["reg_address"], height=80)
    del_address = st.text_area("Delivery Address", value=preset_data["del_address"], height=80)

else:
    client_name = st.text_input("Client Name", placeholder="e.g. Acme Corp (Pty) Ltd")
    trading_name = st.text_input("Trading Name", placeholder="e.g. Acme Store Sandton")
    reg_vat = st.text_input("Co. Reg & VAT", placeholder="Co. Reg: 2023/123456/07 | VAT: 4123456789")
    reg_address = st.text_area("Registered Address", placeholder="Street, Suburb, City, Code", height=80)
    del_address = st.text_area("Delivery Address", placeholder="Delivery Street, Suburb, City, Code", height=80)

st.markdown("---")

# ---------------------------------------------------------
# 3. PRODUCT SPECIFICATION & PRICING
# ---------------------------------------------------------
st.header("3. Product Specification & Line Items")

num_products = st.number_input("How many products / line items?", min_value=1, max_value=20, value=1, step=1)

products = []

for i in range(int(num_products)):
    st.subheader(f"Product #{i+1}")
    p_col1, p_col2 = st.columns([1, 3])
    with p_col1:
        sku = st.text_input(f"SKU Code #{i+1}", value=f"SKU-00{i+1}", key=f"sku_{i}")
    with p_col2:
        desc = st.text_input(f"Full Product Description #{i+1}", value="600ml Food Flask - Plain SS304 Body Configuration" if i == 0 else "", key=f"desc_{i}")
    
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        qty = st.number_input(f"Quantity #{i+1}", min_value=1, value=1000 if i == 0 else 1, step=1, key=f"qty_{i}")
    with q_col2:
        unit_price = st.number_input(f"Unit Price Excl. VAT (R) #{i+1}", min_value=0.0, value=155.32 if i == 0 else 0.0, step=0.01, format="%.2f", key=f"price_{i}")
    
    # Calculate line financials
    subtotal_line = qty * unit_price
    vat_line = subtotal_line * 0.15
    total_line = subtotal_line + vat_line
    
    products.append({
        "SKU": sku,
        "Description": desc,
        "Qty": qty,
        "Unit Price (Excl. VAT)": unit_price,
        "Total Excl. VAT": subtotal_line,
        "VAT (15%)": vat_line,
        "Total Incl. VAT": total_line
    })
    st.divider()

# ---------------------------------------------------------
# 4. ONSCREEN LIVE SUMMARY
# ---------------------------------------------------------
st.header("4. Live Invoicing Summary")

# Create dataframe for summary table
df_summary = pd.DataFrame(products)

# Format currency columns for display
df_display = df_summary.copy()
df_display["Unit Price (Excl. VAT)"] = df_display["Unit Price (Excl. VAT)"].apply(lambda x: f"R {x:,.2f}")
df_display["Total Excl. VAT"] = df_display["Total Excl. VAT"].apply(lambda x: f"R {x:,.2f}")
df_display["VAT (15%)"] = df_display["VAT (15%)"].apply(lambda x: f"R {x:,.2f}")
df_display["Total Incl. VAT"] = df_display["Total Incl. VAT"].apply(lambda x: f"R {x:,.2f}")

st.dataframe(df_display, use_container_width=True)

# Calculate Overall Financial Totals
grand_subtotal = sum(p["Total Excl. VAT"] for p in products)
grand_vat = sum(p["VAT (15%)"] for p in products)
grand_total = sum(p["Total Incl. VAT"] for p in products)
deposit_due = grand_total * 0.50

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Subtotal (Excl. VAT)", f"R {grand_subtotal:,.2f}")
m_col2.metric("Total VAT (15%)", f"R {grand_vat:,.2f}")
m_col3.metric("Grand Total (Incl. VAT)", f"R {grand_total:,.2f}")
m_col4.metric("50% Deposit Due", f"R {deposit_due:,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# 5. PDF GENERATION FUNCTION
# ---------------------------------------------------------
def generate_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=normal_style,
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B')
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=normal_style,
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=2,
        textColor=colors.HexColor('#475569')
    )
    
    header_table_data = [
        [Paragraph("PRO FORMA TAX INVOICE", title_style), 
         Paragraph(f"<b>Invoice No:</b> {invoice_num}<br/><b>Date:</b> {invoice_date.strftime('%d %B %Y')}", meta_style)]
    ]
    header_table = Table(header_table_data, colWidths=[300, 222])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))
    
    # Client details block
    client_p = Paragraph(
        f"<b>BILL & SHIP TO:</b><br/>"
        f"<b>{client_name}</b><br/>"
        f"Trading as: {trading_name}<br/>"
        f"{reg_vat}<br/>"
        f"<b>Reg Address:</b> {reg_address}<br/>"
        f"<b>Delivery Address:</b> {del_address}",
        normal_style
    )
    story.append(client_p)
    story.append(Spacer(1, 15))
    
    # Products Table
    table_data = [["SKU", "Description", "Qty", "Unit Price (Excl)", "Total Excl", "VAT (15%)", "Total Incl"]]
    for p in products:
        table_data.append([
            p["SKU"],
            Paragraph(p["Description"], normal_style),
            str(p["Qty"]),
            f"R {p['Unit Price (Excl. VAT)']:,.2f}",
            f"R {p['Total Excl. VAT']:,.2f}",
            f"R {p['VAT (15%)']:,.2f}",
            f"R {p['Total Incl. VAT']:,.2f}"
        ])
        
    p_table = Table(table_data, colWidths=[65, 140, 40, 75, 70, 60, 72])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 15))
    
    # Financial Totals Summary Block
    totals_data = [
        ["Subtotal (Excl. VAT):", f"R {grand_subtotal:,.2f}"],
        ["Total VAT (15%):", f"R {grand_vat:,.2f}"],
        ["Grand Total (Incl. VAT):", f"R {grand_total:,.2f}"],
        ["50% Deposit Payable:", f"R {deposit_due:,.2f}"]
    ]
    t_table = Table(totals_data, colWidths=[150, 100])
    t_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('TEXTCOLOR', (0,2), (1,2), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,3), (1,3), colors.HexColor('#B91C1C')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,3), (1,3), colors.HexColor('#FEF2F2')),
    ]))
    
    # Align totals box to right
    wrapper_table = Table([["", t_table]], colWidths=[272, 250])
    story.append(wrapper_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Download button
pdf_data = generate_pdf()
st.download_button(
    label="📥 Download Pro Forma PDF",
    data=pdf_data,
    file_name=f"Invoice_{invoice_num}_{client_name.replace(' ', '_')}.pdf",
    mime="application/pdf"
)
