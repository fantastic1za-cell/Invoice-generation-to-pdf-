# ==============================================================================
# SCRIPT MODULE : pdf_engine.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 11:45:00 SAST
# LOCKED BY     : Nisaar Ally
# STATUS        : PRODUCTION LOCKED (SARS-Compliant Engine)
# ==============================================================================

import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

import config

class WatermarkCanvas(canvas.Canvas):
    """Custom canvas for background watermark and page numbering."""
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
        self.setFillColor(colors.HexColor("#F5F5F5"))
        self.setFont("Helvetica-Bold", 60)
        self.rotate(30)
        self.drawString(140, 220, "Mr Mobile SA")
        self.restoreState()


def build_banking_section():
    """Builds side-by-side FNB 1 and FNB 2 banking table with explicit SWIFT formatting."""
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('BankHead', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    body_style = ParagraphStyle('BankBody', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor("#111111"))

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
        [Paragraph(fnb1.get('title', 'PRIMARY ACCOUNT'), header_style), Paragraph(fnb2.get('title', 'SECONDARY ACCOUNT'), header_style)],
        [Paragraph(fnb1_text, body_style), Paragraph(fnb2_text, body_style)]
    ]

    bank_table = Table(bank_table_data, colWidths=[270, 270])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#0f1d2f")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#0f1d2f")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8F9FA")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
    ]))
    return bank_table


def generate_sars_pdf(invoice_payload):
    """Generates SARS VAT Act Section 20 compliant PDF with fallback safeguards."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=15, leading=17, textColor=colors.HexColor("#0f1d2f"))
    header_right = ParagraphStyle('HeadRight', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2, textColor=colors.HexColor("#333333"))
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#111111"))

    # Safely extract payload parameters
    doc_type = str(invoice_payload.get("doc_type", "PRO FORMA TAX INVOICE"))
    doc_num = str(invoice_payload.get("invoice_number", "PI-20261002-02"))
    doc_date = str(invoice_payload.get("date", ""))
    client_name = str(invoice_payload.get("client_name", ""))
    client_vat = str(invoice_payload.get("client_vat", ""))

    header_left_text = f"<b>{doc_type}</b><br/><font size=7 color='#666666'>Official Commercial Document | SARS VAT Compliant</font><br/><font size=8 color='#0f1d2f'><b>Ref: {doc_num}</b> | Date: {doc_date}</font>"
    header_right_text = f"<b>SUPPLIER DETAILS</b><br/>" \
                         f"{config.COMPANY_NAME}<br/>" \
                         f"T/A {config.TRADING_NAME}<br/>" \
                         f"VAT Details: {config.VAT_NUMBER}<br/>" \
                         f"EMAIL: {config.CONTACT_EMAIL}<br/>" \
                         f"{config.SUPPLIER_ADDRESS}"

    top_table = Table([[Paragraph(header_left_text, title_style), Paragraph(header_right_text, header_right)]], colWidths=[290, 250])
    top_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(top_table)
    story.append(Spacer(1, 8))

    client_box_text = f"<b>CLIENT & BILLING DETAILS</b><br/>Client Name: {client_name} | Co. Reg / VAT: {client_vat}"
    client_table = Table([[Paragraph(client_box_text, td_style)]], colWidths=[540])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F3F5")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 8))

    # Items Table Construction with Safe Numeric Parsing
    raw_items = invoice_payload.get("items", [])
    item_rows = [[
        Paragraph("<b>Bespoke Product Description</b>", th_style),
        Paragraph("<b>Qty</b>", th_style),
        Paragraph("<b>Unit Price (Excl)</b>", th_style),
        Paragraph("<b>Net Subtotal</b>", th_style),
        Paragraph("<b>Total (Incl VAT)</b>", th_style)
    ]]

    for item in raw_items:
        if isinstance(item, dict):
            desc = str(item.get("desc", ""))
            try:
                qty = int(item.get("qty", 1))
            except (ValueError, TypeError):
                qty = 1
            try:
                price = float(item.get("price", 0.0))
            except (ValueError, TypeError):
                price = 0.0

            net = qty * price
            tot = net * (1 + config.TAX_RATE)

            item_rows.append([
                Paragraph(desc, td_style),
                Paragraph(f"{qty:,}", td_style),
                Paragraph(f"R {price:,.2f}", td_style),
                Paragraph(f"R {net:,.2f}", td_style),
                Paragraph(f"R {tot:,.2f}", td_style)
            ])

    items_table = Table(item_rows, colWidths=[220, 45, 90, 90, 95])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f1d2f")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    story.append(build_banking_section())
    story.append(Spacer(1, 8))

    clause_text = "<b>STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b><br/>" + "<br/>".join([f"• {c}" for c in config.STATUTORY_CLAUSES])
    clause_table = Table([[Paragraph(clause_text, td_style)]], colWidths=[540])
    clause_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(clause_table)

    doc.build(story, canvasmaker=WatermarkCanvas)
    buffer.seek(0)
    return buffer.getvalue()
