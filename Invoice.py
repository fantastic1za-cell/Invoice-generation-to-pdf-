from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

def format_rand(val):
    return f"R {val:,.2f}"

def generate_proforma_invoice(invoice_data, output_filename="Pro_Forma_Tax_Invoice.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Base Typography Styles
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=13)
    heading_style = ParagraphStyle('Heading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10.5)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5)
    right_bold = ParagraphStyle('RightBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=TA_RIGHT)
    right_normal = ParagraphStyle('RightNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=TA_RIGHT)
    center_bold = ParagraphStyle('CenterBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=TA_CENTER)

    story = [
        Paragraph(invoice_data.get("document_title", "PRO FORMA TAX INVOICE"), title_style),
        Spacer(1, 6)
    ]
    
    # 1. Header Information (Supplier & Client)
    sup = invoice_data['supplier']
    cli = invoice_data['client']
    meta = invoice_data['metadata']
    
    left_header = f"""
    <b>SUPPLIER DETAILS</b><br/>
    {sup['name']}<br/>
    {sup['address']}<br/>
    Contact: {sup['contact']}<br/><br/>
    <b>CLIENT & BILLING DETAILS</b><br/>
    {cli['name']}<br/>
    {cli['reg_vat']}<br/>
    Registered Address: {cli['registered_address']}<br/>
    Delivery Addr: {cli['delivery_address']}
    """
    
    right_header = f"""
    <b>INVOICE NO:</b> {meta['invoice_no']}<br/>
    <b>TAX REFERENCE:</b> {meta['tax_ref']}<br/>
    <b>DATE:</b> {meta['date']}<br/>
    <b>SHIPPING MODE:</b> {meta['shipping_mode']}<br/>
    <b>DUE DATE:</b> {meta['due_date']}<br/>
    <b>VALIDITY:</b> {meta['validity']}
    """
    
    header_table = Table([[Paragraph(left_header, body_style), Paragraph(right_header, body_style)]], colWidths=[325, 210])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ]))
    story.extend([header_table, Spacer(1, 4)])
    
    # 2. Line Items Processing
    story.extend([Paragraph("1. COMMERCIAL LINE-ITEM SPECIFICATION", heading_style), Spacer(1, 3)])
    
    item_rows = [
        [
            Paragraph("<b>Bespoke Product Description</b>", body_style),
            Paragraph("<b>Qty</b>", center_bold),
            Paragraph("<b>Unit Price<br/>(Excl. VAT)</b>", right_bold),
            Paragraph("<b>Net Subtotal<br/>(Excl. VAT)</b>", right_bold),
            Paragraph("<b>Total Price<br/>(Incl. VAT)</b>", right_bold)
        ]
    ]
    
    total_net_excl = 0
    total_grand_incl = 0
    total_qty = 0
    
    for item in invoice_data['line_items']:
        qty = item['qty']
        unit_excl = item['unit_price_excl']
        vat_rate = item.get('vat_rate', 0.15)
        
        net_subtotal = qty * unit_excl
        total_incl = net_subtotal * (1 + vat_rate)
        
        total_qty += qty
        total_net_excl += net_subtotal
        total_grand_incl += total_incl
        
        desc_text = f"<b>{item['title']}</b>"
        if item.get('subtext'):
            desc_text += f"<br/><font color='#555555'>{item['subtext']}</font>"
            
        item_rows.append([
            Paragraph(desc_text, body_style),
            Paragraph(f"{qty:,}", center_bold),
            Paragraph(format_rand(unit_excl), right_normal),
            Paragraph(format_rand(net_subtotal), right_normal),
            Paragraph(format_rand(total_incl), right_bold)
        ])
        
    # Line Items Totals Row
    item_rows.append([
        Paragraph("<b>Combined Program Totals</b>", body_style),
        Paragraph(f"<b>{total_qty:,}</b>", center_bold),
        Paragraph("-", right_normal),
        Paragraph(f"<b>{format_rand(total_net_excl)}</b>", right_bold),
        Paragraph(f"<b>{format_rand(total_grand_incl)}</b>", right_bold)
    ])
    
    t1 = Table(item_rows, colWidths=[225, 45, 85, 90, 90])
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F2F2")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FAFAFA")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.extend([t1, Spacer(1, 8)])
    
    # 3. Milestone Payment Schedule
    story.extend([Paragraph("2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE", heading_style), Spacer(1, 3)])
    
    milestone_rows = [
        [
            Paragraph("<b>Payment Milestone Tranche</b>", body_style),
            Paragraph("<b>Share %</b>", center_bold),
            Paragraph("<b>Net Value (Excl. VAT)</b>", right_bold),
            Paragraph("<b>Grand Total (Incl. VAT)</b>", right_bold)
        ]
    ]
    
    for ms in invoice_data['milestones']:
        ms_text = f"<b>{ms['title']}</b>"
        if ms.get('subtext'):
            ms_text += f"<br/><font color='#555555'>{ms['subtext']}</font>"
            
        milestone_rows.append([
            Paragraph(ms_text, body_style),
            Paragraph(ms['share_pct'], center_bold),
            Paragraph(format_rand(ms['net_excl']), right_normal),
            Paragraph(format_rand(ms['grand_incl']), right_bold)
        ])
        
    t2 = Table(milestone_rows, colWidths=[235, 50, 110, 140])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F2F2")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.extend([t2, Spacer(1, 6)])
    
    # Highlight Box (Amount Due Now)
    due_amount = invoice_data.get('amount_due_now', total_grand_incl * 0.5)
    due_text_words = invoice_data.get('amount_due_words', '')
    
    due_box_data = [
        [
            Paragraph(f"<b>TOTAL AMOUNT NOW DUE TO INITIATE MANUFACTURING:</b><br/><font size='6.5'>({due_text_words})</font>", body_style),
            Paragraph(f"<b>{format_rand(due_amount)}</b>", ParagraphStyle('DueRight', parent=right_bold, fontSize=9.5))
        ]
    ]
    t_due = Table(due_box_data, colWidths=[395, 140])
    t_due.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.extend([t_due, Spacer(1, 8)])
    
    # 4. Corporate Banking Details
    bank = invoice_data['banking']
    story.extend([Paragraph("<b>CORPORATE BANKING DETAILS</b>", heading_style), Spacer(1, 3)])
    bank_data = [
        [
            Paragraph("<b>Bank Name</b>", body_bold),
            Paragraph("<b>Account Type</b>", body_bold),
            Paragraph("<b>Account Number</b>", body_bold),
            Paragraph("<b>Branch Code</b>", body_bold)
        ],
        [
            Paragraph(bank['bank_name'], body_style),
            Paragraph(bank['account_type'], body_style),
            Paragraph(bank['account_number'], body_style),
            Paragraph(bank['branch_code'], body_style)
        ]
    ]
    t_bank = Table(bank_data, colWidths=[133, 133, 133, 136])
    t_bank.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.extend([t_bank, Spacer(1, 8)])
    
    # 5. Statutory Clauses
    story.extend([Paragraph("<b>3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b>", heading_style), Spacer(1, 3)])
    for c in invoice_data['clauses']:
        story.extend([Paragraph(f"• {c}", ParagraphStyle('Clause', parent=body_style, fontSize=6.8, leading=8.5)), Spacer(1, 2)])
        
    # Footer
    story.extend([
        Spacer(1, 8),
        Table([
            [
                Paragraph(f"{sup['name']} | {meta['invoice_no']}", ParagraphStyle('F1', parent=body_style, fontSize=6.5, textColor=colors.HexColor("#666666"))),
                Paragraph("Page 1 of 1", ParagraphStyle('F2', parent=right_normal, fontSize=6.5, textColor=colors.HexColor("#666666")))
            ]
        ], colWidths=[435, 100], style=[('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)])
    ])

    doc.build(story)
    
    # Trigger download if running inside Google Colab environment
    try:
        from google.colab import files
        files.download(output_filename)
    except ImportError:
        pass


# ==============================================================================
# DYNAMIC USAGE EXAMPLE: Simply edit this dictionary for new clients / products
# ==============================================================================

sample_invoice_config = {
    "document_title": "PRO FORMA TAX INVOICE",
    "supplier": {
        "name": "IRESQ LA LUCIA PTY LTD T/A MR MOBILE SA",
        "address": "58 Paarlshoop Road, Homestead Park, 2092 Johannesburg",
        "contact": "0687101939 / 0827867712"
    },
    "client": {
        "name": "Twenty-Five Star (Pty) Ltd t/a Pedros Distribution Centre DBN",
        "reg_vat": "Co. Reg: 2022/686760/07 | VAT: 4690317583",
        "registered_address": "33 Aiken Street, Port Shepstone, KZN, 4240",
        "delivery_address": "4-6 Suzuka Road, Westmead, Pinetown, 3608"
    },
    "metadata": {
        "invoice_no": "PI-2026-0928-02-R1",
        "tax_ref": "4960281899",
        "date": "02 October 2026",
        "shipping_mode": "Sea Freight",
        "due_date": "Immediate (Upon Receipt)",
        "validity": "30 Days"
    },
    "line_items": [
        {
            "title": "600ml Food Flask",
            "subtext": "Plain SS304 Body Configuration. Landed DDP Pinetown.",
            "qty": 3000,
            "unit_price_excl": 155.32,
            "vat_rate": 0.15
        }
    ],
    "milestones": [
        {
            "title": "TRANCHE 1: STARTUP DEPOSIT",
            "subtext": "Required to secure materials & commence factory assembly runs.",
            "share_pct": "50%",
            "net_excl": 232980.00,
            "grand_incl": 267927.00
        },
        {
            "title": "TRANCHE 2: PORT RELEASE",
            "subtext": "Payable post-inspection, directly prior to cargo loading in China.",
            "share_pct": "50%",
            "net_excl": 232980.00,
            "grand_incl": 267927.00
        }
    ],
    "amount_due_now": 267927.00,
    "amount_due_words": "Two Hundred and Sixty-Seven Thousand, Nine Hundred and Twenty-Seven Rand, Inclusive of 15% Local Sales VAT",
    "banking": {
        "bank_name": "First National Bank",
        "account_type": "First Business Zero",
        "account_number": "63152083390",
        "branch_code": "256505 (Melville)"
    },
    "clauses": [
        "<b>Exchange Rate Guarantee & Balance Adjustment:</b> The 50% Startup Deposit paid today secures unit pricing for Tranche 1. The final balance is variable post-China loading clearance based on live USD/ZAR rate.",
        "<b>Raw Material Securement:</b> Production planning triggers automatically upon formal reflection of the deposit in our corporate banking treasury.",
        "<b>Origin Loading Protection:</b> Final balance tranche clears post-QC verification prior to cargo loading.",
        "<b>South African Output VAT:</b> Compliant local 15% Output Sales VAT layer isolated in accordance with SARS validation models."
    ]
}

# Run generation
generate_proforma_invoice(sample_invoice_config, "Pro_Forma_Invoice_Dynamic.pdf")
