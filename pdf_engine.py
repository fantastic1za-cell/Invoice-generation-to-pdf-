# ==============================================================================
# SCRIPT MODULE : pdf_engine.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 15:18:00 SAST
# LOCKED BY     : Nisaar Ally
# STATUS        : PRODUCTION LOCKED (SARS-Compliant Engine)
# ==============================================================================

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

import config

class WatermarkCanvas(canvas.Canvas):
    """Custom canvas rendering diagonal background watermark matching Photo 1."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_watermark()
            super().showPage()
        super().save()

    def draw_watermark(self):
        self.saveState()
        self.setFillColor(colors.HexColor("#EAEAEA"))
        self.setFont("Helvetica-Bold", 85)
        self.rotate(28)
        self.drawString(100, 200, "Mr Mobile")
        self.restoreState()


def generate_sars_pdf(invoice_payload):
    """Generates complete SARS VAT Act Section 20 PDF layout as shown in Photo 1."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18,
        rightMargin=18,
        topMargin=18,
        bottomMargin=18
    )

    story = []
    styles = getSampleStyleSheet()

    # Color Definitions from Photo 1
    DARK_NAVY = colors.HexColor("#1A2B4C")
    HEADER_GREY = colors.HexColor("#2C3E50")
    LIGHT_GREY_BG = colors.HexColor("#F4F6F7")
    GOLD_BANNER_BG = colors.HexColor("#FCF3CF")
    GOLD_BANNER_BORDER = colors.HexColor("#F39C12")
    RED_BANNER_BG = colors.HexColor("#FDEDEC")
    RED_BANNER_BORDER = colors.HexColor("#E74C3C")

    # Typography Styles
    title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=18, leading=20, textColor=colors.black)
    title_sub = ParagraphStyle('DocSub', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#555555"))
    header_right = ParagraphStyle('HeadRight', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2, textColor=colors.HexColor("#333333"))
    
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#111111"))
    td_bold = ParagraphStyle('TDBold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#111111"))
    
    sec_head = ParagraphStyle('SecHead', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.black)
    banner_text = ParagraphStyle('BannerTxt', fontName='Helvetica-Bold', fontSize=10, leading=12, alignment=1, textColor=colors.HexColor("#900C3F"))

    # Extract Data Payload Safely
    doc_type = str(invoice_payload.get("doc_type", "PRO FORMA TAX INVOICE"))
    doc_num = str(invoice_payload.get("invoice_number", "PI-20261002-02"))
    doc_date = str(invoice_payload.get("date", "2026-10-02"))
    shipping_mode = str(invoice_payload.get("shipping_mode", "Sea Freight"))
    
    client_name = str(invoice_payload.get("client_name", "Twenty-Five Star (Pty) Ltd"))
    trading_name = str(invoice_payload.get("client_trading", "Pedros Distribution Centre DBN"))
    client_reg_vat = str(invoice_payload.get("client_vat", "Co. Reg: 2022/686760/07 | VAT: 4690317583"))
    reg_address = str(invoice_payload.get("reg_address", "33 Aiken Street, Port Shepstone, KZN, 4240"))
    delivery_address = str(invoice_payload.get("delivery_address", "4-6 Suzuka Road, Westmead, Pinetown, 3608"))

    # 1. HEADER SECTION
    header_left_text = f"<b>{doc_type}</b><br/><font size=7 color='#555555'>Official Commercial Document | SARS VAT Compliant</font>"
    header_right_text = f"<b>SUPPLIER DETAILS</b><br/>" \
                         f"{config.COMPANY_NAME}<br/>" \
                         f"T/A {config.TRADING_NAME}<br/>" \
                         f"VAT Details: {config.VAT_NUMBER}<br/>" \
                         f"EMAIL: <a href='mailto:{config.CONTACT_EMAIL}' color='#0066cc'>{config.CONTACT_EMAIL}</a><br/>" \
                         f"{config.SUPPLIER_ADDRESS}<br/>" \
                         f"<b>Contact:</b> <a href='tel:+27687101939' color='#0066cc'>068 710 1939</a> / <a href='https://wa.me/27827867712' color='#25D366'>082 786 7712 (WhatsApp)</a>"

    top_table = Table([[Paragraph(header_left_text, title_style), Paragraph(header_right_text, header_right)]], colWidths=[280, 276])
    top_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(top_table)
    story.append(Spacer(1, 6))

    # 2. CLIENT & BILLING DETAILS BOX
    client_box_text = f"<b>CLIENT & BILLING DETAILS</b><br/>" \
                      f"<b>Client Name:</b> {client_name}<br/>" \
                      f"<b>Trading Name:</b> {trading_name}<br/>" \
                      f"<b>Co. Reg & VAT:</b> {client_reg_vat}<br/>" \
                      f"<b>Reg Address:</b> {reg_address}<br/>" \
                      f"<b>Delivery Addr:</b> {delivery_address}"

    client_table = Table([[Paragraph(client_box_text, td_style)]], colWidths=[556])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GREY_BG),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 6))

    # 3. TRANSACTION METADATA BAR (7 Columns)
    meta_headers = ["INVOICE NO", "TAX REFERENCE", "DATE", "SHIPPING", "DUE DATE", "VALIDITY", "US$/ZAR FX"]
    meta_values = [
        doc_num,
        config.VAT_NUMBER,
        doc_date,
        shipping_mode,
        "Immediate (Upon Receipt)",
        "30 days",
        "R 16.67"
    ]

    meta_data = [
        [Paragraph(f"<b>{h}</b>", th_style) for h in meta_headers],
        [Paragraph(v, td_style) for v in meta_values]
    ]

    meta_table = Table(meta_data, colWidths=[80, 80, 65, 75, 95, 80, 81])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HEADER_GREY),
        ('BACKGROUND', (0,1), (-1,1), LIGHT_GREY_BG),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 4. COMMERCIAL LINE-ITEM SPECIFICATION TABLE
    story.append(Paragraph("<b>1. COMMERCIAL LINE-ITEM SPECIFICATION</b>", sec_head))
    story.append(Spacer(1, 3))

    raw_items = invoice_payload.get("items", [])
    item_rows = [[
        Paragraph("<b>Bespoke Product Description</b>", th_style),
        Paragraph("<b>Qty</b>", th_style),
        Paragraph("<b>Unit Price<br/>(Excl. VAT)</b>", th_style),
        Paragraph("<b>Net Subtotal<br/>(Excl. VAT)</b>", th_style),
        Paragraph("<b>Total Price<br/>(Incl. VAT)</b>", th_style)
    ]]

    tot_qty = 0
    tot_subtotal = 0.0
    tot_grand = 0.0

    for item in raw_items:
        if isinstance(item, dict):
            desc = str(item.get("desc", "600ml Food Flask\nPlain SS304 Body Configuration. Landed DDP Pinetown."))
            qty = int(item.get("qty", 3000))
            price = float(item.get("price", 155.32))
            net = qty * price
            tot = net * (1 + config.TAX_RATE)

            tot_qty += qty
            tot_subtotal += net
            tot_grand += tot

            desc_p = desc.replace("\n", "<br/>")
            item_rows.append([
                Paragraph(desc_p, td_style),
                Paragraph(f"{qty:,}", td_style),
                Paragraph(f"R {price:,.2f}", td_style),
                Paragraph(f"R {net:,.2f}", td_style),
                Paragraph(f"R {tot:,.2f}", td_style)
            ])

    # Summary Row
    item_rows.append([
        Paragraph("<b>Combined Program Totals (MOQ Run)</b>", td_bold),
        Paragraph(f"<b>{tot_qty:,}</b>", td_bold),
        Paragraph("", td_bold),
        Paragraph(f"<b>R {tot_subtotal:,.2f}</b>", td_bold),
        Paragraph(f"<b>R {tot_grand:,.2f}</b>", td_bold)
    ])

    items_table = Table(item_rows, colWidths=[246, 50, 80, 90, 90])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EAECEE")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8))

    # 5. CONTRACTUAL MILESTONE PAYMENT SCHEDULE TABLE
    story.append(Paragraph("<b>2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE</b>", sec_head))
    story.append(Spacer(1, 3))

    tranche1_sub = tot_subtotal * 0.50
    tranche1_tot = tot_grand * 0.50
    tranche2_sub = tot_subtotal * 0.50
    tranche2_tot = tot_grand * 0.50

    sched_rows = [
        [
            Paragraph("<b>Payment Milestone Tranche</b>", th_style),
            Paragraph("<b>Share %</b>", th_style),
            Paragraph("<b>Net Value<br/>(Excl. VAT)</b>", th_style),
            Paragraph("<b>Grand Total<br/>(Incl. VAT)</b>", th_style)
        ],
        [
            Paragraph("<b>TRANCHE 1: STARTUP DEPOSIT</b><br/><font size=7 color='#555555'>Required to secure materials & commerce factory assembly runs.</font>", td_style),
            Paragraph("50%", td_style),
            Paragraph(f"R {tranche1_sub:,.2f}", td_style),
            Paragraph(f"R {tranche1_tot:,.2f}", td_style)
        ],
        [
            Paragraph("<b>TRANCHE 2: PORT RELEASE BALANCE</b><br/><font size=7 color='#555555'>Payable post-inspection, prior to loading in China.</font>", td_style),
            Paragraph("50%", td_style),
            Paragraph(f"R {tranche2_sub:,.2f}", td_style),
            Paragraph(f"R {tranche2_tot:,.2f}*", td_style)
        ]
    ]

    sched_table = Table(sched_rows, colWidths=[276, 60, 110, 110])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HEADER_GREY),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sched_table)
    story.append(Spacer(1, 6))

    # 6. TOTAL AMOUNT NOW DUE BANNER (Red Highlight Box)
    due_text = f"TOTAL AMOUNT NOW DUE TO INITIATE MANUFACTURING (TRANCHE 1 DEPOSIT)<br/><b>R {tranche1_tot:,.2f}</b>"
    due_table = Table([[Paragraph(due_text, banner_text)]], colWidths=[556])
    due_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), RED_BANNER_BG),
        ('BOX', (0,0), (-1,-1), 1, RED_BANNER_BORDER),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(due_table)
    story.append(Spacer(1, 6))

    # 7. PAYMENT & FOREIGN EXCHANGE TERMS BANNER (Gold Highlight Box)
    fx_text = f"<font size=7.5 color='#7D6608'><b>Payment & Foreign Exchange Terms:</b> The 50% initial startup deposit (Tranche 1: R {tranche1_tot:,.2f} Incl. VAT) is absorbed and locked at current pricing upon payment. The remaining 50% balance (Tranche 2) will be adjusted based on the active foreign exchange (FX) rate at the time of final port release payment.</font>"
    fx_table = Table([[Paragraph(fx_text, td_style)]], colWidths=[556])
    fx_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GOLD_BANNER_BG),
        ('BOX', (0,0), (-1,-1), 0.8, GOLD_BANNER_BORDER),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(fx_table)
    story.append(Spacer(1, 6))

    # 8. OFFICIAL DUAL FNB BANKING TABLE
    fnb1 = config.BANKING_DETAILS.get("PRIMARY_ACCOUNT", {})
    fnb2 = config.BANKING_DETAILS.get("SECONDARY_ACCOUNT", {})

    fnb1_text = f"<b>Account Name:</b> {fnb1.get('account_name', '')}<br/>" \
                f"<b>Bank:</b> {fnb1.get('bank', '')}<br/>" \
                f"<b>Account Type:</b> {fnb1.get('account_type', '')}<br/>" \
                f"<b>Account No:</b> {fnb1.get('account_number', '')}<br/>" \
                f"<b>Branch Code:</b> {fnb1.get('branch_code', '')} | <b>SWIFT:</b> {fnb1.get('swift_code', 'FIRNZAJJ')}"

    fnb2_text = f"<b>Account Name:</b> {fnb2.get('account_name', '')}<br/>" \
                f"<b>Bank:</b> {fnb2.get('bank', '')}<br/>" \
                f"<b>Account Type:</b> {fnb2.get('account_type', '')}<br/>" \
                f"<b>Account No:</b> {fnb2.get('account_number', '')}<br/>" \
                f"<b>Branch Code:</b> {fnb2.get('branch_code', '')} | <b>SWIFT:</b> {fnb2.get('swift_code', 'FIRNZAJJ')}"

    bank_table_data = [
        [Paragraph(fnb1.get('title', 'OFFICIAL CORPORATE ACCOUNT (FNB 1)'), th_style), Paragraph(fnb2.get('title', 'FRANCHISE BUSINESS ACCOUNT (FNB 2)'), th_style)],
        [Paragraph(fnb1_text, td_style), Paragraph(fnb2_text, td_style)]
    ]

    bank_table = Table(bank_table_data, colWidths=[278, 278])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), DARK_NAVY),
        ('BACKGROUND', (1,0), (1,0), DARK_NAVY),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT_GREY_BG),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
    ]))
    story.append(bank_table)
    story.append(Spacer(1, 6))

    # 9. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES
    story.append(Paragraph("<b>3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b>", sec_head))
    story.append(Spacer(1, 2))

    clause_text = "<br/>".join([f"• <b>{c.split(':')[0]}:</b>{c.split(':')[1]}" if ":" in c else f"• {c}" for c in config.STATUTORY_CLAUSES])
    clause_table = Table([[Paragraph(f"<font size=7 color='#333333'>{clause_text}</font>", td_style)]], colWidths=[556])
    clause_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GREY_BG),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(clause_table)

    # Build PDF using custom watermark canvas
    doc.build(story, canvasmaker=WatermarkCanvas)
    buffer.seek(0)
    return buffer.getvalue()
