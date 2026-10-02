# ==============================================================================
# SCRIPT NAME: pdf_engine.py
# TIMESTAMP: 2026-10-02 15:40:00 SAST
# STATUS: LOCKED & ENTERPRISE-GRADE (WATERMARK & HEADER LOGO INTEGRATED)
# ==============================================================================

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas that draws the centered whitewashed watermark logo 
    on the page background, along with professional page numbering.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_watermark_and_footer(num_pages)
            super().showPage()
        super().save()

    def draw_watermark_and_footer(self, total_pages):
        self.saveState()
        
        # 1. Whitewashed Background Watermark Logo (Centered, light opacity/wash)
        logo_path = "mmsalogo.png.jpg"
        if os.path.exists(logo_path):
            try:
                self.setFillAlpha(0.08)  # Light whitewashed opacity
                # Draw centered on A4 page (Width: 595.27, Height: 841.89)
                img_width = 300
                img_height = 300
                x_pos = (595.27 - img_width) / 2
                y_pos = (841.89 - img_height) / 2
                self.drawImage(logo_path, x_pos, y_pos, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
                
        self.restoreState()


def build_pdf_document(data):
    import io
    buffer = io.BytesIO()
    
    # Document Setup (A4 with professional margins)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_COLOR = colors.HexColor("#0F172A")    # Deep Navy
    SECONDARY_COLOR = colors.HexColor("#334155")  # Slate Grey
    ACCENT_COLOR = colors.HexColor("#B91C1C")     # Crimson Red
    LIGHT_BG = colors.HexColor("#F8FAFC")         # Light Grey Background
    BORDER_COLOR = colors.HexColor("#CBD5E1")     # Border Grey

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR
    )
    
    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=SECONDARY_COLOR
    )

    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY_COLOR
    )

    body_bold = ParagraphStyle(
        'TableBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY_COLOR
    )

    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    # ==========================================
    # HEADER SECTION: LOGO & SUPPLIER DETAILS
    # ==========================================
    logo_path = "mmsalogo.png.jpg"
    if os.path.exists(logo_path):
        # Logo centered at 45px height
        logo_img = Image(logo_path, width=45, height=45)
        logo_img.hAlign = 'CENTER'
        story.append(logo_img)
        # Exactly 5px spacing below the logo as requested
        story.append(Spacer(1, 5))

    supplier = SUPPLIER_DETAILS if 'SUPPLIER_DETAILS' in globals() else {
        "entity": "IRESQ LA LUCIA PTY LTD",
        "trading": "T/A MR MOBILE SA",
        "vat": "4960281899",
        "email": "nisaar@fantastic1.com",
        "address": "58 Paarlshoop Road, Homestead Park, 2092 Johannesburg, South Africa",
        "contact": "068 710 1939 / 082 786 7712"
    }

    header_data = [
        [
            Paragraph(f"<b>{data.get('document_type', 'PRO FORMA TAX INVOICE')}</b>", title_style),
            Paragraph(
                f"<b>SUPPLIER DETAILS</b><br/>"
                f"{supplier.get('entity', 'IRESQ LA LUCIA PTY LTD')}<br/>"
                f"{supplier.get('trading', 'T/A MR MOBILE SA')}<br/>"
                f"<b>VAT Details:</b> {supplier.get('vat', '4960281899')}<br/>"
                f"<b>EMAIL:</b> {supplier.get('email', 'nisaar@fantastic1.com')}<br/>"
                f"{supplier.get('address', '')}<br/>"
                f"<b>Contact:</b> {supplier.get('contact', '')}",
                sub_title_style
            )
        ],
        [
            Paragraph("Official Commercial Document | SARS VAT Compliant", sub_title_style),
            ""
        ]
    ]

    header_table = Table(header_data, colWidths=[270, 252])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('SPAN', (1,0), (1,1)),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # CLIENT & BILLING DETAILS
    # ==========================================
    client = data.get('client', {})
    client_data = [
        [Paragraph("<b>CLIENT & BILLING DETAILS</b>", header_style)],
        [Paragraph(
            f"<b>Client Name:</b> {client.get('client_name', '')}<br/>"
            f"<b>Trading Name:</b> {client.get('trading_name', '')}<br/>"
            f"<b>Co. Reg & VAT:</b> {client.get('reg_vat', '')}<br/>"
            f"<b>Reg Address:</b> {client.get('reg_address', '')}<br/>"
            f"<b>Delivery Addr:</b> {client.get('del_address', '')}",
            body_style
        )]
    ]
    client_table = Table(client_data, colWidths=[522])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), PRIMARY_COLOR),
        ('BACKGROUND', (0,1), (0,1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # META DETAILS TABLE (Invoice No, Date, Validity, Exchange Rate)
    # ==========================================
    meta_headers = [
        Paragraph("INVOICE NO", header_style),
        Paragraph("TAX REFERENCE", header_style),
        Paragraph("DATE", header_style),
        Paragraph("SHIPPING", header_style),
        Paragraph("DUE DATE", header_style),
        Paragraph("VALIDITY", header_style),
        Paragraph("US$/ZAR FX", header_style)
    ]
    meta_values = [
        Paragraph(str(data.get('invoice_num', '')), body_bold),
        Paragraph(supplier.get('vat', '4960281899'), body_style),
        Paragraph(str(data.get('invoice_date', '')), body_style),
        Paragraph(str(data.get('shipping_mode', '')), body_style),
        Paragraph(str(data.get('due_date', '')), body_style),
        Paragraph(str(data.get('validity', '')), body_style),
        Paragraph(f"<b>{data.get('exchange_rate_display', '')}</b>", body_bold)
    ]
    meta_table = Table([meta_headers, meta_values], colWidths=[75, 75, 70, 75, 80, 65, 82])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
        ('BACKGROUND', (0,1), (-1,1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # ==========================================
    # 1. COMMERCIAL LINE-ITEM SPECIFICATION
    # ==========================================
    story.append(Paragraph("<b>1. COMMERCIAL LINE-ITEM SPECIFICATION</b>", body_bold))
    story.append(Spacer(1, 4))

    line_headers = [
        Paragraph("Bespoke Product Description", header_style),
        Paragraph("Qty", header_style),
        Paragraph("Unit Price<br/>(Excl. VAT)", header_style),
        Paragraph("Net Subtotal<br/>(Excl. VAT)", header_style),
        Paragraph("Total Price<br/>(Incl. VAT)", header_style)
    ]
    
    line_rows = [line_headers]
    grand_excl = 0.0
    grand_incl = 0.0

    for prod in data.get('products', []):
        net_sub = prod['Qty'] * prod['Unit Price (Excl)']
        tot_inc = net_sub * 1.15
        grand_excl += net_sub
        grand_incl += tot_inc

        line_rows.append([
            Paragraph(f"<b>{prod['SKU']}</b><br/>{prod['Description']}", body_style),
            Paragraph(f"{prod['Qty']:,.0f}", body_style),
            Paragraph(f"R {prod['Unit Price (Excl)']:,.2f}", body_style),
            Paragraph(f"R {net_sub:,.2f}", body_style),
            Paragraph(f"R {tot_inc:,.2f}", body_style)
        ])

    line_rows.append([
        Paragraph("<b>Combined Program Totals (MOQ Run)</b>", body_bold),
        Paragraph(f"<b>{sum(p['Qty'] for p in data.get('products', [])):,.0f}</b>", body_bold),
        Paragraph("", body_style),
        Paragraph(f"<b>R {grand_excl:,.2f}</b>", body_bold),
        Paragraph(f"<b>R {grand_incl:,.2f}</b>", body_bold)
    ])

    line_table = Table(line_rows, colWidths=[202, 55, 85, 90, 90])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('BACKGROUND', (0,-1), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 12))

    # ==========================================
    # 2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE
    # ==========================================
    tranche1 = grand_incl * 0.50
    tranche2 = grand_incl * 0.50

    story.append(Paragraph("<b>2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE</b>", body_bold))
    story.append(Spacer(1, 4))

    sched_headers = [
        Paragraph("Payment Milestone Tranche", header_style),
        Paragraph("Share %", header_style),
        Paragraph("Net Value<br/>(Excl. VAT)", header_style),
        Paragraph("Grand Total<br/>(Incl. VAT)", header_style)
    ]
    sched_rows = [
        sched_headers,
        [
            Paragraph("<b>TRANCHE 1: STARTUP DEPOSIT</b><br/>Required to secure materials & commerce factory assembly runs.", body_style),
            Paragraph("50%", body_style),
            Paragraph(f"R {tranche1 / 1.15:,.2f}", body_style),
            Paragraph(f"R {tranche1:,.2f}", body_style)
        ],
        [
            Paragraph("<b>TRANCHE 2: PORT RELEASE BALANCE</b><br/>Payable post-inspection, prior to loading in China.", body_style),
            Paragraph("50%", body_style),
            Paragraph(f"R {tranche2 / 1.15:,.2f}", body_style),
            Paragraph(f"R {tranche2:,.2f}*", body_style)
        ]
    ]
    sched_table = Table(sched_rows, colWidths=[252, 60, 105, 105])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sched_table)
    story.append(Spacer(1, 8))

    # Total Due Banner
    due_banner_data = [[
        Paragraph(
            f"<font color='#B91C1C'><b>TOTAL AMOUNT NOW DUE TO INITIATE MANUFACTURING (TRANCHE 1 DEPOSIT)</b></font><br/>"
            f"<font size=12><b>R {tranche1:,.2f}</b></font>",
            ParagraphStyle('DueBanner', parent=styles['Normal'], alignment=1, fontSize=10, leading=14)
        )
    ]]
    due_banner_table = Table(due_banner_data, colWidths=[522])
    due_banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
        ('BOX', (0,0), (-1,-1), 1, ACCENT_COLOR),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(due_banner_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # PAYMENT & FOREIGN EXCHANGE TERMS (Extracted from Photo 2)
    # ==========================================
    fx_terms_text = (
        f"<b>Payment & Foreign Exchange Terms:</b> The 50% initial startup deposit "
        f"(Tranche 1: R {tranche1:,.2f} Incl. VAT) is absorbed and locked at current pricing upon payment. "
        f"The remaining 50% balance (Tranche 2) will be adjusted based on the active foreign exchange (FX) "
        f"rate at the time of final port release payment."
    )
    fx_table = Table([[Paragraph(fx_terms_text, body_style)]], colWidths=[522])
    fx_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(fx_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # BANKING DETAILS
    # ==========================================
    bank_p = data.get('bank_details_primary', BANK_DETAILS_PRIMARY)
    bank_s = data.get('bank_details_secondary', BANK_DETAILS_SECONDARY)

    bank_headers = [
        Paragraph("OFFICIAL CORPORATE ACCOUNT (FNB 1)", header_style),
        Paragraph("FRANCHISE BUSINESS ACCOUNT (FNB 2)", header_style)
    ]
    bank_rows = [
        bank_headers,
        [
            Paragraph(
                f"<b>Account Name:</b> {bank_p.get('account_name', '')}<br/>"
                f"<b>Bank:</b> {bank_p.get('bank_name', '')}<br/>"
                f"<b>Account Type:</b> {bank_p.get('account_type', '')}<br/>"
                f"<b>Account No:</b> {bank_p.get('account_number', '')}<br/>"
                f"<b>Branch Code:</b> {bank_p.get('branch_code', '')}",
                body_style
            ),
            Paragraph(
                f"<b>Account Name:</b> {bank_s.get('account_name', '')}<br/>"
                f"<b>Bank:</b> {bank_s.get('bank_name', '')}<br/>"
                f"<b>Account Type:</b> {bank_s.get('account_type', '')}<br/>"
                f"<b>Account No:</b> {bank_s.get('account_number', '')}<br/>"
                f"<b>Branch Code:</b> {bank_s.get('branch_code', '')} | <b>SWIFT:</b> {bank_s.get('swift', '')}",
                body_style
            )
        ]
    ]
    bank_table = Table(bank_rows, colWidths=[261, 261])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('BACKGROUND', (0,1), (-1,1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(bank_table)
    story.append(Spacer(1, 10))

    # ==========================================
    # 3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES (Extracted from Photo 2)
    # ==========================================
    compliance_content = [
        Paragraph("<b>3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b>", header_style),
        Paragraph(
            "• <b>Raw Material Securement:</b> Production planning, custom material blending, and machine line configurations will trigger "
            "automatically upon formal reflection of the 50% Tranche 1 deposit inside our corporate banking treasury. The 50% initial startup "
            "pricing is absorbed and fixed as billed.<br/>"
            "• <b>Origin Loading Protection & FX Adjustment:</b> The final 50% balance tranche is contractually tied to origin quality control (QC) "
            "verification prior to container loading in China. The final balance payment will be calculated based on the prevailing foreign "
            "exchange (FX) rate at the time of transaction settlement.",
            body_style
        )
    ]
    compliance_table = Table(compliance_content, colWidths=[522])
    compliance_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), SECONDARY_COLOR),
        ('BACKGROUND', (0,1), (0,1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether(compliance_table))

    # Build PDF using NumberedCanvas for watermark and headers
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
