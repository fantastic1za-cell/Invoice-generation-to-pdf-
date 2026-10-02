import streamlit as st
import pandas as pd
from datetime import datetime
import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set page config
st.set_page_config(page_title="MR MOBILE SA - Pro Forma Generator", page_icon="📄", layout="wide")

# ---------------------------------------------------------
# CONSTANTS & PRESETS
# ---------------------------------------------------------
SUPPLIER_DETAILS = {
    "company": "IRESQ LA LUCIA PTY LTD",
    "trading": "MR MOBILE SA",
    "address": "58 Paarlshoop Road, Homestead Park, 2092 Johannesburg, South Africa",
    "contact": "068 710 1939 / 082 786 7712",
    "tax_ref": "4960281899"
}

BANK_DETAILS = {
    "bank_name": "First National Bank",
    "account_type": "First Business Zero",
    "account_number": "63152083390",
    "branch_code": "256505 (Melville)"
}

PRESET_CLIENTS = {
    "Twenty-Five Star (Pty) Ltd (Pedros DBN)": {
        "client_name": "Twenty-Five Star (Pty) Ltd",
        "trading_name": "Pedros Distribution Centre DBN",
        "reg_vat": "Co. Reg: 2022/686760/07 | VAT: 4690317583",
        "reg_address": "33 Aiken Street, Port Shepstone, KZN, 4240",
        "del_address": "4-6 Suzuka Road, Westmead, Pinetown, 3608"
    }
}

# Number to words helper function for Rand amounts
def number_to_words_rand(amount):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def _convert_nn(n):
        if n < 20: return units[n]
        for i, t in enumerate(tens):
            if i >= 2 and n < (i + 1) * 10:
                rest = units[n - i * 10]
                return f"{t}-{rest}" if rest else t
        return ""

    def _convert_nnn(n):
        word = ""
        rem = n % 100
        hundreds = n // 100
        if hundreds > 0:
            word = f"{units[hundreds]} Hundred"
            if rem > 0: word += f" and {_convert_nn(rem)}"
        else:
            word = _convert_nn(rem)
        return word

    int_val = int(round(amount))
    if int_val == 0: return "Zero Rand"
    
    thousands = (int_val // 1000) % 1000
    millions = (int_val // 1000000) % 1000
    hundreds = int_val % 1000
    
    res = []
    if millions: res.append(f"{_convert_nnn(millions)} Million")
    if thousands: res.append(f"{_convert_nnn(thousands)} Thousand")
    if hundreds: res.append(f"{_convert_nnn(hundreds)}")
    
    return " ".join(res) + " Rand, Inclusive of 15% Local Sales VAT"

st.title("📄 Pro Forma Tax Invoice Generator")
st.caption(f"Supplier: **{SUPPLIER_DETAILS['company']} t/a {SUPPLIER_DETAILS['trading']}** | Tax Ref: **{SUPPLIER_DETAILS['tax_ref']}**")

# ---------------------------------------------------------
# 1. INVOICE META & SHIPPING
# ---------------------------------------------------------
st.header("1. Document Metadata")
col1, col2, col3, col4 = st.columns(4)
with col1:
    invoice_date = st.date_input("Invoice Date", datetime.today())
    invoice_num = st.text_input("Invoice Number", f"PI-{invoice_date.strftime('%Y-%m%d')}-02")
with col2:
    shipping_mode = st.selectbox("Shipping Mode", ["Sea Freight", "Air Freight", "Road Express", "Local Collection"])
    due_date_str = st.text_input("Due Date", "Immediate (Upon Receipt)")
with col3:
    validity_str = st.text_input("Validity", "30 Days")
    tax_ref = st.text_input("Tax Reference / VAT", SUPPLIER_DETAILS["tax_ref"])
with col4:
    st.info(f"**Bank:** {BANK_DETAILS['bank_name']}\n\n**Acc:** {BANK_DETAILS['account_number']}\n\n**Branch:** {BANK_DETAILS['branch_code']}")

st.markdown("---")

# ---------------------------------------------------------
# 2. CLIENT & DELIVERY DETAILS
# ---------------------------------------------------------
st.header("2. Client & Billing Details")
client_option = st.radio("Client Details Source:", ["Existing Client (Preset)", "New Client Entry"], horizontal=True)

if client_option == "Existing Client (Preset)":
    selected_preset = st.selectbox("Select Preset Client:", list(PRESET_CLIENTS.keys()))
    preset = PRESET_CLIENTS[selected_preset]
    client_name = st.text_input("Client Legal Name", value=preset["client_name"])
    trading_name = st.text_input("Trading Name", value=preset["trading_name"])
    reg_vat = st.text_input("Co. Reg & VAT", value=preset["reg_vat"])
    reg_address = st.text_area("Registered Address", value=preset["reg_address"], height=70)
    del_address = st.text_area("Delivery Address", value=preset["del_address"], height=70)
else:
    client_name = st.text_input("Client Legal Name", placeholder="e.g. Twenty-Five Star (Pty) Ltd")
    trading_name = st.text_input("Trading Name", placeholder="e.g. Pedros Distribution Centre DBN")
    reg_vat = st.text_input("Co. Reg & VAT", placeholder="Co. Reg: 2022/686760/07 | VAT: 4690317583")
    reg_address = st.text_area("Registered Address", placeholder="33 Aiken Street, Port Shepstone, KZN, 4240", height=70)
    del_address = st.text_area("Delivery Address", placeholder="4-6 Suzuka Road, Westmead, Pinetown, 3608", height=70)

st.markdown("---")

# ---------------------------------------------------------
# 3. DYNAMIC PRODUCTS & LINE ITEMS
# ---------------------------------------------------------
st.header("3. Commercial Line-Item Specification")
num_products = st.number_input("How many products / line items?", min_value=1, max_value=10, value=1, step=1)

products = []
for i in range(int(num_products)):
    st.subheader(f"Item #{i+1}")
    p1, p2 = st.columns([1, 3])
    with p1:
        sku = st.text_input(f"SKU / Item Code #{i+1}", value="600ml Food Flask" if i == 0 else f"ITEM-00{i+1}", key=f"sku_{i}")
    with p2:
        desc = st.text_input(f"Bespoke Description #{i+1}", value="Plain SS304 Body Configuration. Landed DDP Pinetown." if i == 0 else "", key=f"desc_{i}")
    
    q1, q2 = st.columns(2)
    with q1:
        qty = st.number_input(f"Quantity (Units) #{i+1}", min_value=1, value=3000 if i == 0 else 1, step=1, key=f"qty_{i}")
    with q2:
        unit_price = st.number_input(f"Unit Price Excl. VAT (R) #{i+1}", min_value=0.0, value=155.32 if i == 0 else 0.0, step=0.01, format="%.2f", key=f"price_{i}")
    
    subtotal_excl = qty * unit_price
    vat_amt = subtotal_excl * 0.15
    total_incl = subtotal_excl + vat_amt
    
    products.append({
        "SKU": sku,
        "Description": desc,
        "Qty": qty,
        "Unit Price (Excl)": unit_price,
        "Net Subtotal (Excl)": subtotal_excl,
        "VAT (15%)": vat_amt,
        "Total Price (Incl)": total_incl
    })

st.markdown("---")

# ---------------------------------------------------------
# 4. LIVE ONSCREEN INVOICING SUMMARY
# ---------------------------------------------------------
st.header("4. Live Invoice & Milestone Calculation")

df_products = pd.DataFrame(products)
df_display = df_products.copy()
df_display["Unit Price (Excl)"] = df_display["Unit Price (Excl)"].apply(lambda x: f"R {x:,.2f}")
df_display["Net Subtotal (Excl)"] = df_display["Net Subtotal (Excl)"].apply(lambda x: f"R {x:,.2f}")
df_display["VAT (15%)"] = df_display["VAT (15%)"].apply(lambda x: f"R {x:,.2f}")
df_display["Total Price (Incl)"] = df_display["Total Price (Incl)"].apply(lambda x: f"R {x:,.2f}")

st.dataframe(df_display, use_container_width=True)

grand_excl = sum(p["Net Subtotal (Excl)"] for p in products)
grand_vat = sum(p["VAT (15%)"] for p in products)
grand_incl = sum(p["Total Price (Incl)"] for p in products)

tranche1_excl = grand_excl * 0.50
tranche1_incl = grand_incl * 0.50

c1, c2, c3, c4 = st.columns(4)
c1.metric("Net Program Subtotal (Excl)", f"R {grand_excl:,.2f}")
c2.metric("Total VAT (15%)", f"R {grand_vat:,.2f}")
c3.metric("Grand Total (Incl. VAT)", f"R {grand_incl:,.2f}")
c4.metric("TRANCHE 1 DEPOSIT (50%)", f"R {tranche1_incl:,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# 5. SINGLE-PAGE A4 PDF GENERATION ENGINE
# ---------------------------------------------------------
def generate_pdf():
    buffer = io.BytesIO()
    # Narrow margins to strictly fit single A4 page
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28
    )
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    
    style_title = ParagraphStyle('DocTitle', parent=normal, fontName='Helvetica-Bold', fontSize=15, leading=17, textColor=colors.HexColor('#0F172A'))
    style_subtitle = ParagraphStyle('SubTitle', parent=normal, fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#475569'))
    style_supplier = ParagraphStyle('SuppText', parent=normal, fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1E293B'))
    style_meta_hdr = ParagraphStyle('MetaHdr', parent=normal, fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.HexColor('#64748B'), alignment=1)
    style_meta_val = ParagraphStyle('MetaVal', parent=normal, fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#0F172A'), alignment=1)
    
    style_cell = ParagraphStyle('CellText', parent=normal, fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#0F172A'))
    style_cell_bold = ParagraphStyle('CellTextBold', parent=normal, fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#0F172A'))
    style_cell_right = ParagraphStyle('CellTextRight', parent=normal, fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#0F172A'), alignment=2)
    style_cell_right_bold = ParagraphStyle('CellTextRightBold', parent=normal, fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#0F172A'), alignment=2)
    
    # Header: Title & Supplier Details
    head_data = [
        [
            Paragraph(f"<b>PRO FORMA TAX INVOICE</b><br/><font size=7 color='#64748B'>Official Commercial Document | SARS VAT Compliant</font>", style_title),
            Paragraph(
                f"<b>SUPPLIER DETAILS</b><br/>"
                f"<b>{SUPPLIER_DETAILS['company']}</b><br/>"
                f"T/A {SUPPLIER_DETAILS['trading']}<br/>"
                f"{SUPPLIER_DETAILS['address']}<br/>"
                f"Contact: {SUPPLIER_DETAILS['contact']}",
                style_supplier
            )
        ]
    ]
    head_table = Table(head_data, colWidths=[270, 269])
    head_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT')
    ]))
    story.append(head_table)
    story.append(Spacer(1, 6))
    
    # Client & Billing Block
    client_box_data = [
        [
            Paragraph(
                f"<b>CLIENT & BILLING DETAILS</b><br/>"
                f"<b>{client_name}</b><br/>"
                f"Trading Name: {trading_name}<br/>"
                f"{reg_vat}<br/>"
                f"<b>Reg Address:</b> {reg_address}<br/>"
                f"<b>Delivery Addr:</b> {del_address}",
                style_supplier
            )
        ]
    ]
    client_table = Table(client_box_data, colWidths=[539])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 6))
    
    # Document Metadata Bar
    meta_data = [
        [
            Paragraph("INVOICE NO", style_meta_hdr),
            Paragraph("TAX REFERENCE", style_meta_hdr),
            Paragraph("DATE", style_meta_hdr),
            Paragraph("SHIPPING MODE", style_meta_hdr),
            Paragraph("DUE DATE", style_meta_hdr),
            Paragraph("VALIDITY", style_meta_hdr)
        ],
        [
            Paragraph(invoice_num, style_meta_val),
            Paragraph(tax_ref, style_meta_val),
            Paragraph(invoice_date.strftime('%d %B %Y'), style_meta_val),
            Paragraph(shipping_mode, style_meta_val),
            Paragraph(due_date_str, style_meta_val),
            Paragraph(validity_str, style_meta_val)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[90, 85, 95, 85, 100, 84])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))
    
    # 1. Commercial Line-Item Table
    story.append(Paragraph(f"<b>1. COMMERCIAL LINE-ITEM SPECIFICATION ({shipping_mode.upper()} MOQ RUN)</b>", style_subtitle))
    story.append(Spacer(1, 3))
    
    item_table_data = [
        [
            Paragraph("Bespoke Product Description", ParagraphStyle('IH1', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke)),
            Paragraph("Qty", ParagraphStyle('IH2', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke, alignment=1)),
            Paragraph("Unit Price<br/>(Excl. VAT)", ParagraphStyle('IH3', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke, alignment=2)),
            Paragraph("Net Subtotal<br/>(Excl. VAT)", ParagraphStyle('IH4', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke, alignment=2)),
            Paragraph("Total Price<br/>(Incl. VAT)", ParagraphStyle('IH5', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke, alignment=2))
        ]
    ]
    
    total_qty = 0
    for p in products:
        total_qty += p["Qty"]
        desc_p = Paragraph(f"<b>{p['SKU']}</b><br/><font color='#475569'>{p['Description']}</font>", style_cell)
        item_table_data.append([
            desc_p,
            Paragraph(f"{p['Qty']:,}", ParagraphStyle('C1', parent=style_cell, alignment=1)),
            Paragraph(f"R {p['Unit Price (Excl)']:,.2f}", style_cell_right),
            Paragraph(f"R {p['Net Subtotal (Excl)']:,.2f}", style_cell_right),
            Paragraph(f"R {p['Total Price (Incl)']:,.2f}", style_cell_right)
        ])
        
    # Program Totals Row
    item_table_data.append([
        Paragraph("<b>Combined Program Totals (MOQ Run)</b>", style_cell_bold),
        Paragraph(f"<b>{total_qty:,}</b>", ParagraphStyle('C2', parent=style_cell_bold, alignment=1)),
        Paragraph("", style_cell),
        Paragraph(f"<b>R {grand_excl:,.2f}</b>", style_cell_right_bold),
        Paragraph(f"<b>R {grand_incl:,.2f}</b>", style_cell_right_bold)
    ])
    
    item_table = Table(item_table_data, colWidths=[229, 50, 80, 90, 90])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F8FAFC')),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 8))
    
    # 2. Milestone Payment Schedule
    story.append(Paragraph("<b>2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE</b>", style_subtitle))
    story.append(Spacer(1, 3))
    
    m_data = [
        [
            Paragraph("Payment Milestone Tranche", ParagraphStyle('MH1', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke)),
            Paragraph("Share %", ParagraphStyle('MH2', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke, alignment=1)),
            Paragraph("Net Value<br/>(Excl. VAT)", ParagraphStyle('MH3', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke, alignment=2)),
            Paragraph("Grand Total<br/>(Incl. VAT)", ParagraphStyle('MH4', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke, alignment=2))
        ],
        [
            Paragraph("<b>TRANCHE 1: STARTUP DEPOSIT</b><br/><font color='#475569'>Required to secure materials & commence factory assembly runs. Pricing locked & absorbed as billed.</font>", style_cell),
            Paragraph("<b>50%</b>", ParagraphStyle('MC1', parent=style_cell_bold, alignment=1)),
            Paragraph(f"R {tranche1_excl:,.2f}", style_cell_right),
            Paragraph(f"<b>R {tranche1_incl:,.2f}</b>", style_cell_right_bold)
        ],
        [
            Paragraph("<b>TRANCHE 2: PORT RELEASE BALANCE</b><br/><font color='#475569'>Payable post-inspection, prior to loading in China. Balance subject to prevailing exchange rate at time of loading.</font>", style_cell),
            Paragraph("<b>50%</b>", ParagraphStyle('MC2', parent=style_cell_bold, alignment=1)),
            Paragraph(f"R {tranche1_excl:,.2f}*", style_cell_right),
            Paragraph(f"R {tranche1_incl:,.2f}*", style_cell_right)
        ]
    ]
    m_table = Table(m_data, colWidths=[269, 50, 110, 110])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 6))
    
    # Highlighted Total Deposit Box
    words_str = number_to_words_rand(tranche1_incl)
    deposit_box_data = [
        [
            Paragraph(
                f"<font size=7 color='#B91C1C'><b>TOTAL AMOUNT NOW DUE TO INITIATE MANUFACTURING (TRANCHE 1 DEPOSIT)</b></font><br/>"
                f"<font size=6.5 color='#475569'>({words_str})</font><br/>"
                f"<font size=12 color='#B91C1C'><b>R {tranche1_incl:,.2f}</b></font>",
                ParagraphStyle('DepStyle', parent=normal, alignment=1, leading=11)
            )
        ]
    ]
    dep_table = Table(deposit_box_data, colWidths=[539])
    dep_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#FCA5A5')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(dep_table)
    story.append(Spacer(1, 6))
    
    # Terms Note & FNB Banking Details Table
    story.append(Paragraph(
        f"<font size=6.5 color='#475569'><b>Payment & Foreign Exchange Terms:</b> The 50% initial startup deposit (Tranche 1: R {tranche1_incl:,.2f} Incl. VAT) is absorbed and "
        f"locked at current pricing upon payment. The remaining 50% balance (Tranche 2) will be adjusted based on the active foreign exchange (FX) rate at the time of final port release payment.</font>",
        normal
    ))
    story.append(Spacer(1, 5))
    
    # Bank Table
    bank_table_data = [
        [
            Paragraph("<b>FNB CORPORATE BANKING DETAILS (OFFICIAL ACCOUNT)</b>", ParagraphStyle('BH', parent=normal, fontName='Helvetica-Bold', fontSize=7, textColor=colors.whitesmoke))
        ],
        [
            Paragraph(
                f"<b>Bank Name:</b> {BANK_DETAILS['bank_name']} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Account Type:</b> {BANK_DETAILS['account_type']} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Account Number:</b> <font color='#0F172A'><b>{BANK_DETAILS['account_number']}</b></font> &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Branch Code:</b> {BANK_DETAILS['branch_code']}",
                ParagraphStyle('BC', parent=normal, fontName='Helvetica', fontSize=7, textColor=colors.HexColor('#1E293B'), alignment=1)
            )
        ]
    ]
    bank_table = Table(bank_table_data, colWidths=[539])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(bank_table)
    story.append(Spacer(1, 6))
    
    # 3. Statutory Clauses
    story.append(Paragraph("<b>3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b>", style_subtitle))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "<font size=6 color='#475569'>"
        "<b>Raw Material Securement:</b> Production planning, custom material blending, and machine line configurations will trigger automatically upon formal reflection of the 50% Tranche 1 deposit inside our corporate banking treasury. The 50% initial startup pricing is absorbed and fixed as billed.<br/>"
        "<b>Origin Loading Protection & FX Adjustment:</b> The final 50% balance tranche is contractually tied to origin quality control (QC) verification prior to container loading in China. The final balance payment will be calculated based on the prevailing foreign exchange (FX) rate at the time of transaction settlement."
        "</font>",
        normal
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Download button
pdf_data = generate_pdf()
st.download_button(
    label="📥 Download Pro Forma PDF (A4 Single Page)",
    data=pdf_data,
    file_name=f"Pro_Forma_Invoice_{invoice_num}_{client_name.replace(' ', '_')}.pdf",
    mime="application/pdf"
)
