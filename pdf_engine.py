# ==============================================================================
# SCRIPT NAME: pdf_engine.py
# TIMESTAMP: 2026-10-02 23:30:00 SAST
# STATUS: CLICKABLE LINKS (EMAIL/CALL/WA) + 3-LINE SPACING BEFORE CLIENT DETAILS
# ==============================================================================

import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Draws full-page background logo watermark at 0.15 opacity 
    (2x lighter opacity for crisp text legibility).
    """
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
        logo_path = "mmsalogo.png.jpg"
        if os.path.exists(logo_path):
            try:
                self.setFillAlpha(0.15)
                page_w, page_h = 595.27, 841.89
                self.drawImage(
                    logo_path, 
                    0, 
                    0, 
                    width=page_w, 
                    height=page_h, 
                    preserveAspectRatio=True, 
                    mask='auto'
                )
            except Exception:
                pass
        self.restoreState()


def build_pdf_document(data):
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    story = []
    styles = getSampleStyleSheet()

    PRIMARY_COLOR = colors.HexColor("#0F172A")
    SECONDARY_COLOR = colors.HexColor("#334155")
    ACCENT_COLOR = colors.HexColor("#B91C1C")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#CBD5E1")

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=PRIMARY_COLOR)
    sub_title_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=SECONDARY_COLOR)
    body_style = ParagraphStyle('TableBody', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=PRIMARY_COLOR)
    body_bold = ParagraphStyle('TableBodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=PRIMARY_COLOR)
    header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)

    # 1. Supplier Details Header with Links & Line Breaks
    supplier = data.get('supplier_details', {})
    
    email_addr = supplier.get('email', 'nisaar@fantastic1.com')
    phone_call_display = supplier.get('phone_call', '068 710 1939')
    phone_call_raw = supplier.get('phone_call_raw', '+27687101939')
    phone_wa_display = supplier.get('phone_wa', '082 786 7712')
    phone_wa_raw = supplier.get('phone_wa_raw', '27827867712')
    
    address_l1 = supplier.get('address_line1', '58 Paarlshoop Road, Homestead Park, 2092')
    address_l2 = supplier.get('address_line2', 'Johannesburg, South Africa')

    supplier_formatted_text = (
        f"<b>SUPPLIER DETAILS</b><br/>"
        f"{supplier.get('entity', '')}<br/>"
        f"{supplier.get('trading', '')}<br/>"
        f"<b>VAT Details:</b> {supplier.get('vat', '')}<br/>"
        f"<b>EMAIL:</b> <a href=\"mailto:{email_addr}\" color=\"#0284C7\"><u>{email_addr}</u></a><br/>"
        f"{address_l1}<br/>"
        f"{address_l2}<br/>"
        f"<b>Contact:</b> <a href=\"tel:{phone_call_raw}\" color=\"#0284C7\"><u>{phone_call_display}</u></a> / "
        f"<a href=\"https://wa.me/{phone_wa_raw}\" color=\"#16A34A\"><u>{phone_wa_display} (WhatsApp)</u></a>"
    )

    header_data = [
        [
            Paragraph(f"<b>{data.get('document_type', 'PRO FORMA TAX INVOICE')}</b>", title_style),
            Paragraph(supplier_formatted_text, sub_title_style)
        ],
        [
            Paragraph("Official Commercial Document | SARS VAT Compliant", sub_title_style),
            Paragraph("", sub_title_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[285, 270])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('SPAN', (1,0), (1,1)), ('BOTTOMPADDING', (0,0), (-1,-1), 0)]))
    story.append(header_table)

    # Leave 3 blank lines (24pt space) after contact details before Client Billing Details
    story.append(Spacer(1, 24))

    # 2. Client & Billing Details Table
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
    client_table = Table(client_data, colWidths=[555])
    client_table.setStyle(TableStyle([('BACKGROUND', (0,0), (0,0), PRIMARY_COLOR), ('BACKGROUND', (0,1), (0,1), LIGHT_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3)]))
    story.append(client_table)
    story.append(Spacer(1, 6))

    # 3. Document Meta Details Table
    show_fx = data.get('show_fx_on_output', True)
    
    if show_fx:
        meta_headers = [Paragraph("INVOICE NO", header_style), Paragraph("TAX REFERENCE", header_style), Paragraph("DATE", header_style), Paragraph("SHIPPING", header_style), Paragraph("DUE DATE", header_style), Paragraph("VALIDITY", header_style), Paragraph("US$/ZAR FX", header_style)]
        meta_values = [
            Paragraph(str(data.get('invoice_num', '')), body_bold),
            Paragraph(str(supplier.get('vat', '')), body_style),
            Paragraph(str(data.get('invoice_date', '')), body_style),
            Paragraph(str(data.get('shipping_mode', '')), body_style),
            Paragraph(str(data.get('due_date', '')), body_style),
            Paragraph(str(data.get('validity', '')), body_style),
            Paragraph(f"<b>{data.get('exchange_rate_display', '')}</b>", body_bold)
        ]
        meta_table = Table([meta_headers, meta_values], colWidths=[80, 80, 75, 80, 85, 70, 85])
    else:
        meta_headers = [Paragraph("INVOICE NO", header_style), Paragraph("TAX REFERENCE", header_style), Paragraph("DATE", header_style), Paragraph("SHIPPING", header_style), Paragraph("DUE DATE", header_style), Paragraph("VALIDITY", header_style)]
        meta_values = [
            Paragraph(str(data.get('invoice_num', '')), body_bold),
            Paragraph(str(supplier.get('vat', '')), body_style),
            Paragraph(str(data.get('invoice_date', '')), body_style),
            Paragraph(str(data.get('shipping_mode', '')), body_style),
            Paragraph(str(data.get('due_date', '')), body_style),
            Paragraph(str(data.get('validity', '')), body_style)
        ]
        meta_table = Table([meta_headers, meta_values], colWidths=[95, 95, 85, 95, 100, 85])

    meta_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR), ('BACKGROUND', (0,1), (-1,1), LIGHT_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 3)]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # 4. Commercial Line Items
    story.append(Paragraph("<b>1. COMMERCIAL LINE-ITEM SPECIFICATION</b>", body_bold))
    story.append(Spacer(1, 2))

    line_headers = [Paragraph("Bespoke Product Description", header_style), Paragraph("Qty", header_style), Paragraph("Unit Price<br/>(Excl. VAT)", header_style), Paragraph("Net Subtotal<br/>(Excl. VAT)", header_style), Paragraph("Total Price<br/>(Incl. VAT)", header_style)]
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
    line_table = Table(line_rows, colWidths=[225, 55, 90, 90, 95])
    line_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR), ('BACKGROUND', (0,-1), (-1,-1), LIGHT_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 3)]))
    story.append(line_table)
    story.append(Spacer(1, 6))

    # 5. Contractual Milestone Payment Schedule
    tranche1 = grand_incl * 0.50
    tranche2 = grand_incl * 0.50

    story.append(Paragraph("<b>2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE</b>", body_bold))
    story.append(Spacer(1, 2))

    sched_headers = [Paragraph("Payment Milestone Tranche", header_style), Paragraph("Share %", header_style), Paragraph("Net Value<br/>(Excl. VAT)", header_style), Paragraph("Grand Total<br/>(Incl. VAT)", header_style)]
    sched_rows = [
        sched_headers,
        [Paragraph("<b>TRANCHE 1: STARTUP DEPOSIT</b><br/>Required to secure materials & commerce factory assembly runs.", body_style), Paragraph("50%", body_style), Paragraph(f"R {tranche1 / 1.15:,.2f}", body_style), Paragraph(f"R {tranche1:,.2f}", body_style)],
        [Paragraph("<b>TRANCHE 2: PORT RELEASE BALANCE</b><br/>Payable post-inspection, prior to loading in China.", body_style), Paragraph("50%", body_style), Paragraph(f"R {tranche2 / 1.15:,.2f}", body_style), Paragraph(f"R {tranche2:,.2f}*", body_style)]
    ]
    sched_table = Table(sched_rows, colWidths=[265, 60, 115, 115])
    sched_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 3)]))
    story.append(sched_table)
    story.append(Spacer(1, 6))

    # Total Due Banner
    due_banner_data = [[Paragraph(f"<font color='#B91C1C'><b>TOTAL AMOUNT NOW DUE TO INITIATE MANUFACTURING (TRANCHE 1 DEPOSIT)</b></font><br/><font size=10><b>R {tranche1:,.2f}</b></font>", ParagraphStyle('DueBanner', parent=styles['Normal'], alignment=1, fontSize=8.5, leading=11))]]
    due_banner_table = Table(due_banner_data, colWidths=[555])
    due_banner_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")), ('BOX', (0,0), (-1,-1), 1, ACCENT_COLOR), ('PADDING', (0,0), (-1,-1), 4), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(due_banner_table)
    story.append(Spacer(1, 6))

    # 6. Payment & FX Terms
    if show_fx:
        fx_terms_text = (
            f"<b>Payment & Foreign Exchange Terms:</b> The 50% initial startup deposit "
            f"(Tranche 1: R {tranche1:,.2f} Incl. VAT) is absorbed and locked at current pricing upon payment. "
            f"The remaining 50% balance (Tranche 2) will be adjusted based on the active foreign exchange (FX) "
            f"rate at the time of final port release payment."
        )
        fx_table = Table([[Paragraph(fx_terms_text, body_style)]], colWidths=[555])
        fx_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")), ('PADDING', (0,0), (-1,-1), 3)]))
        story.append(fx_table)
        story.append(Spacer(1, 6))

    # 7. Banking Details Table
    bank_p = data.get('bank_details_primary', {})
    bank_s = data.get('bank_details_secondary', {})

    bank_headers = [Paragraph("OFFICIAL CORPORATE ACCOUNT (FNB 1)", header_style), Paragraph("FRANCHISE BUSINESS ACCOUNT (FNB 2)", header_style)]
    bank_rows = [
        bank_headers,
        [
            Paragraph(f"<b>Account Name:</b> {bank_p.get('account_name', '')}<br/><b>Bank:</b> {bank_p.get('bank_name', '')}<br/><b>Account Type:</b> {bank_p.get('account_type', '')}<br/><b>Account No:</b> {bank_p.get('account_number', '')}<br/><b>Branch Code:</b> {bank_p.get('branch_code', '')}", body_style),
            Paragraph(f"<b>Account Name:</b> {bank_s.get('account_name', '')}<br/><b>Bank:</b> {bank_s.get('bank_name', '')}<br/><b>Account Type:</b> {bank_s.get('account_type', '')}<br/><b>Account No:</b> {bank_s.get('account_number', '')}<br/><b>Branch Code:</b> {bank_s.get('branch_code', '')} | <b>SWIFT:</b> {bank_s.get('swift', '')}", body_style)
        ]
    ]
    bank_table = Table(bank_rows, colWidths=[277.5, 277.5])
    bank_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR), ('BACKGROUND', (0,1), (-1,1), LIGHT_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 3)]))
    story.append(bank_table)
    story.append(Spacer(1, 6))

    # 8. Statutory Compliance
    compliance_content = [
        [Paragraph("<b>3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b>", header_style)],
        [Paragraph(
            "• <b>Raw Material Securement:</b> Production planning, custom material blending, and machine line configurations will trigger "
            "automatically upon formal reflection of the 50% Tranche 1 deposit inside our corporate banking treasury. The 50% initial startup "
            "pricing is absorbed and fixed as billed.<br/>"
            "• <b>Origin Loading Protection & FX Adjustment:</b> The final 50% balance tranche is contractually tied to origin quality control (QC) "
            "verification prior to container loading in China. The final balance payment will be calculated based on the prevailing foreign "
            "exchange (FX) rate at the time of transaction settlement.",
            body_style
        )]
    ]
    compliance_table = Table(compliance_content, colWidths=[555])
    compliance_table.setStyle(TableStyle([('BACKGROUND', (0,0), (0,0), SECONDARY_COLOR), ('BACKGROUND', (0,1), (0,1), LIGHT_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 3)]))
    story.append(KeepTogether(compliance_table))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
