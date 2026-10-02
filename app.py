import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
import io
import os
import json
from datetime import datetime

# --- SEQUENTIAL INVOICE NUMBER GENERATOR ---
COUNTER_FILE = "invoice_counter.json"

def get_next_invoice_number():
    today_date = datetime.now().strftime("%Y-%m-%d")
    date_code = datetime.now().strftime("%Y-%m%d") # Format: YYYY-MMDD
    
    data = {"date": today_date, "count": 0}
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass

    # If same day, increment count; if new day, reset to 1
    if data.get("date") == today_date:
        data["count"] += 1
    else:
        data["date"] = today_date
        data["count"] = 1

    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f)

    seq_str = f"{data['count']:03d}"
    return f"PI-{date_code}-{seq_str}"

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Pro Forma Invoice Generator", layout="centered")

st.title("📄 Commercial Pro Forma Generator")
st.caption("Auto-calculates VAT, 50% milestone deposits, and tracks sequential daily invoice numbers.")

# Generate initial sequential number for display
if "current_inv_no" not in st.session_state:
    st.session_state["current_inv_no"] = get_next_invoice_number()

with st.form("invoice_form"):
    st.subheader("1. Invoice Identification")
    inv_no = st.text_input("Invoice Number (Auto-Generated)", value=st.session_state["current_inv_no"])
    inv_date = st.text_input("Invoice Date", value=datetime.now().strftime("%d %B %Y"))
    
    st.subheader("2. Client & Delivery Details")
    client_name = st.text_input("Client Name", "Twenty-Five Star (Pty) Ltd")
    client_trading = st.text_input("Trading Name", "Pedros Distribution Centre DBN")
    client_vat = st.text_input("Co. Reg & VAT", "Co. Reg: 2022/686760/07 | VAT: 4690317583")
    reg_addr = st.text_input("Registered Address", "33 Aiken Street, Port Shepstone, KZN, 4240")
    del_addr = st.text_input("Delivery Address", "4-6 Suzuka Road, Westmead, Pinetown, 3608")
    
    st.subheader("3. Product Specification & Pricing")
    prod_title = st.text_input("Product Description", "600ml Food Flask")
    prod_subtext = st.text_input("Line Specification", "Plain SS304 Body Configuration. Landed DDP Pinetown.")
    col1, col2 = st.columns(2)
    with col1:
        qty = st.number_input("Quantity", value=3000, step=100)
    with col2:
        unit_price = st.number_input("Unit Price Excl. VAT (Rand)", value=155.32, step=1.0)
    
    submitted = st.form_submit_button("Generate & Download PDF")

if submitted:
    # Math Calculations
    net_total = qty * unit_price
    grand_total = net_total * 1.15
    tranche_net = net_total * 0.5
    tranche_grand = grand_total * 0.5
    
    # PDF Document Construction
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=13)
    sub_title = ParagraphStyle('SubTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor("#555555"))
    heading_style = ParagraphStyle('Heading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10.5)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=7.2, leading=9)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.2, leading=9)
    right_bold = ParagraphStyle('RightBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.2, leading=9, alignment=TA_RIGHT)
    right_normal = ParagraphStyle('RightNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=7.2, leading=9, alignment=TA_RIGHT)
    center_bold = ParagraphStyle('CenterBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.2, leading=9, alignment=TA_CENTER)

    story = [
        Paragraph("PRO FORMA TAX INVOICE", title_style),
        Paragraph("Official Commercial Document | SARS VAT Compliant", sub_title),
        Spacer(1, 6)
    ]
    
    # Header Information
    left_header = f"""
    <b>SUPPLIER DETAILS</b><br/>
    IRESQ LA LUCIA PTY LTD T/A MR MOBILE SA<br/>
    58 Paarlshoop Road, Homestead Park, 2092 JHB<br/>
    Contact: 068 710 1939 / 082 786 7712<br/><br/>
    <b>CLIENT & BILLING DETAILS</b><br/>
    {client_name}<br/>
    Trading Name: {client_trading}<br/>
    {client_vat}<br/>
    Reg Address: {reg_addr}<br/>
    Delivery Addr: {del_addr}
    """
    
    right_header = f"""
    <b>INVOICE NO:</b> {inv_no}<br/>
    <b>TAX REFERENCE:</b> 4960281899<br/>
    <b>DATE:</b> {inv_date}<br/>
    <b>SHIPPING MODE:</b> Sea Freight<br/>
    <b>DUE DATE:</b> Immediate (Upon Receipt)<br/>
    <b>VALIDITY:</b> 30 Days
    """
    
    header_table = Table([[Paragraph(left_header, body_style), Paragraph(right_header, body_style)]], colWidths=[330, 205])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ]))
    story.extend([header_table, Spacer(1, 4)])
    
    # 1. Commercial Line Item
    story.extend([Paragraph("1. COMMERCIAL LINE-ITEM SPECIFICATION (SEA FREIGHT MOQ RUN)", heading_style), Spacer(1, 3)])
    item_rows = [
        [
            Paragraph("<b>Bespoke Product Description</b>", body_style),
            Paragraph("<b>Qty</b>", center_bold),
            Paragraph("<b>Unit Price<br/>(Excl. VAT)</b>", right_bold),
            Paragraph("<b>Net Subtotal<br/>(Excl. VAT)</b>", right_bold),
            Paragraph("<b>Total Price<br/>(Incl. VAT)</b>", right_bold)
        ],
        [
            Paragraph(f"<b>{prod_title}</b><br/><font color='#555555'>{prod_subtext}</font>", body_style),
            Paragraph(f"{qty:,}", center_bold),
            Paragraph(f"R {unit_price:,.2f}", right_normal),
            Paragraph(f"R {net_total:,.2f}", right_normal),
            Paragraph(f"R {grand_total:,.2f}", right_bold)
        ],
        [
            Paragraph("<b>Combined Program Totals (MOQ Run)</b>", body_style),
            Paragraph(f"<b>{qty:,}</b>", center_bold),
            Paragraph("", right_normal),
            Paragraph(f"<b>R {net_total:,.2f}</b>", right_bold),
            Paragraph(f"<b>R {grand_total:,.2f}</b>", right_bold)
        ]
    ]
    t1 = Table(item_rows, colWidths=[225, 45, 85, 90, 90])
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F2F2")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))
    story.extend([t1, Spacer(1, 6)])

    # 2. Milestones Schedule
    story.extend([Paragraph("2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE", heading_style), Spacer(1, 3)])
    milestone_rows = [
        [
            Paragraph("<b>Payment Milestone Tranche</b>", body_style),
            Paragraph("<b>Share %</b>", center_bold),
            Paragraph("<b>Net Value<br/>(Excl. VAT)</b>", right_bold),
            Paragraph("<b>Grand Total<br/>(Incl. VAT)</b>", right_bold)
        ],
        [
            Paragraph("<b>TRANCHE 1: STARTUP DEPOSIT</b><br/><font color='#555555'>Required to secure materials & commence factory assembly runs.<br/>Pricing locked & absorbed as billed.</font>", body_style),
            Paragraph("50%", center_bold),
            Paragraph(f"R {tranche_net:,.2f}", right_normal),
            Paragraph(f"R {tranche_grand:,.2f}", right_bold)
        ],
        [
            Paragraph("<b>TRANCHE 2: PORT RELEASE BALANCE</b><br/><font color='#555555'>Payable post-inspection, prior to loading in China. Balance subject to prevailing exchange rate at time of loading.</font>", body_style),
            Paragraph("50%", center_bold),
            Paragraph(f"R {tranche_net:,.2f}*", right_normal),
            Paragraph(f"R {tranche_grand:,.2f}*", right_bold)
        ]
    ]
    t2 = Table(milestone_rows, colWidths=[235, 50, 110, 140])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F2F2")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))
    story.extend([t2, Spacer(1, 6)])

    # Amount Due Box
    due_box_data = [
        [
            Paragraph("<b>TOTAL AMOUNT NOW DUE TO INITIATE MANUFACTURING (TRANCHE 1 DEPOSIT):</b>", body_style),
            Paragraph(f"<b>R {tranche_grand:,.2f}</b>", ParagraphStyle('DueRight', parent=right_bold, fontSize=10))
        ],
        [
            Paragraph(f"<font size='6.2' color='#444444'><b>Payment & Foreign Exchange Terms:</b> The 50% initial startup deposit (Tranche 1: R {tranche_grand:,.2f} Incl. VAT) is absorbed and locked at current pricing upon payment. The remaining 50% balance (Tranche 2) will be adjusted based on the active foreign exchange (FX) rate at the time of final port release payment.</font>", body_style),
            Paragraph("", body_style)
        ]
    ]
    t_due = Table(due_box_data, colWidths=[395, 140])
    t_due.setStyle(TableStyle([
        ('SPAN', (0, 1), (1, 1)),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))
    story.extend([t_due, Spacer(1, 6)])

    # Banking Block
    story.extend([Paragraph("<b>FNB CORPORATE BANKING DETAILS (OFFICIAL ACCOUNT)</b>", heading_style), Spacer(1, 3)])
    t_bank = Table([
        [Paragraph("<b>Bank Name</b>", body_bold), Paragraph("<b>Account Type</b>", body_bold), Paragraph("<b>Account Number</b>", body_bold), Paragraph("<b>Branch Code</b>", body_bold)],
        [Paragraph("First National Bank", body_style), Paragraph("First Business Zero", body_style), Paragraph("63152083390", body_style), Paragraph("256505 (Melville)", body_style)]
    ], colWidths=[133, 133, 133, 136])
    t_bank.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.extend([t_bank, Spacer(1, 6)])

    # Clauses
    story.extend([Paragraph("<b>3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b>", heading_style), Spacer(1, 3)])
    clauses = [
        "<b>Raw Material Securement:</b> Production planning, custom material blending, and machine line configurations will trigger automatically upon formal reflection of the 50% Tranche 1 deposit inside our corporate banking treasury.",
        "<b>Origin Loading Protection & FX Adjustment:</b> The final 50% balance tranche is contractually tied to origin quality control (QC) verification prior to container loading in China."
    ]
    for c in clauses:
        story.extend([Paragraph(f"• {c}", ParagraphStyle('Clause', parent=body_style, fontSize=6.5, leading=8.2)), Spacer(1, 2)])
        
    story.extend([
        Spacer(1, 6),
        Table([
            [
                Paragraph(f"Iresq La Lucia Pty Ltd t/a Mr Mobile SA | Pro Forma Invoice {inv_no}", ParagraphStyle('F1', parent=body_style, fontSize=6.5, textColor=colors.HexColor("#666666"))),
                Paragraph("Page 1 of 1", ParagraphStyle('F2', parent=right_normal, fontSize=6.5, textColor=colors.HexColor("#666666")))
            ]
        ], colWidths=[435, 100], style=[('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)])
    ])

    doc.build(story)
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    
    # Save a local server copy automatically
    filename = f"{inv_no}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_data)

    st.success(f"Invoice {inv_no} Created & Saved!")
    
    # Instant device download button
    st.download_button(
        label=f"⬇️ Tap to Download {filename}",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf"
    )
    
    # Update next sequential invoice number for the next submission
    st.session_state["current_inv_no"] = get_next_invoice_number()

