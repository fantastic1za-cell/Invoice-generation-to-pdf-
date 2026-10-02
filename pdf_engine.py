"""
ReportLab PDF Generation Engine with Centered Watermark, Bold Exchange Rate Block, and Dual Banking.
"""
import io
import os
import logging
from typing import Dict, Any
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from config import SUPPLIER_DETAILS
from helpers import number_to_words_rand

logger = logging.getLogger("DocumentGenerator")

def draw_watermark(canvas, doc):
    """Draws a subtle whitewashed logo watermark centered on the page canvas."""
    canvas.saveState()
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            # Center of A4 is width=595.27, height=841.89
            img_width = 250
            img_height = 120
            x = (595.27 - img_width) / 2
            y = (841.89 - img_height) / 2
            canvas.setFillAlpha(0.12)  # Light whitewash transparency
            canvas.drawImage(logo_path, x, y, width=img_width, height=img_height, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    canvas.restoreState()

def build_pdf_document(invoice_data: Dict[str, Any], enforce_single_page: bool = True) -> io.BytesIO:
    buffer = io.BytesIO()
    
    top_margin = 18 if enforce_single_page else 36
    bottom_margin = 18 if enforce_single_page else 36
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )
    
    story = []
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    
    doc_type = invoice_data.get("document_type", "PRO FORMA TAX INVOICE")
    
    style_title = ParagraphStyle('DocTitle', parent=normal, fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#0F172A'))
    style_supplier = ParagraphStyle('SuppText', parent=normal, fontName='Helvetica', fontSize=6.5, leading=8, textColor=colors.HexColor('#1E293B'))
    style_meta_hdr = ParagraphStyle('MetaHdr', parent=normal, fontName='Helvetica-Bold', fontSize=5.5, leading=7, textColor=colors.HexColor('#64748B'), alignment=1)
    style_meta_val = ParagraphStyle('MetaVal', parent=normal, fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.HexColor('#0F172A'), alignment=1)
    
    style_cell = ParagraphStyle('CellText', parent=normal, fontName='Helvetica', fontSize=6.5, leading=8, textColor=colors.HexColor('#0F172A'))
    style_cell_bold = ParagraphStyle('CellTextBold', parent=normal, fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.HexColor('#0F172A'))
    style_cell_right = ParagraphStyle('CellTextRight', parent=normal, fontName='Helvetica', fontSize=6.5, leading=8, textColor=colors.HexColor('#0F172A'), alignment=2)
    style_cell_right_bold = ParagraphStyle('CellTextRightBold', parent=normal, fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.HexColor('#0F172A'), alignment=2)

    # 1. Header with Centered Logo positioning & Supplier Details
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            logo_flowable = Image(logo_path, width=75, height=36)
            logo_flowable.hAlign = 'CENTER'
        except Exception:
            logo_flowable = Paragraph("<b>MR MOBILE SA</b>", style_title)
    else:
        logo_flowable = Paragraph("<b>MR MOBILE SA</b>", style_title)

    head_data = [
        [
            logo_flowable,
            Paragraph(f"<b>{doc_type}</b><br/><font size=6 color='#64748B'>Official Commercial Document | SARS Compliant</font>", style_title),
            Paragraph(
                f"<b>SUPPLIER DETAILS</b><br/>"
                f"<b>{SUPPLIER_DETAILS['company']}</b><br/>"
                f"T/A {SUPPLIER_DETAILS['trading']}<br/>"
                f"<b>VAT Details:</b> {SUPPLIER_DETAILS['vat_no']}<br/>"
                f"<b>EMAIL:</b> {SUPPLIER_DETAILS['email']}<br/>"
                f"{SUPPLIER_DETAILS['address']}<br/>"
                f"Contact: {SUPPLIER_DETAILS['contact']}",
                style_supplier
            )
        ]
    ]
    head_table = Table(head_data, colWidths=[80, 200, 267])
    head_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'), 
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT')
    ]))
    story.append(head_table)
    story.append(Spacer(1, 4))

    # 2. Client Details
    client = invoice_data.get("client", {})
    client_box_data = [[
        Paragraph(
            f"<b>CLIENT & BILLING DETAILS</b><br/>"
            f"<b>{client.get('client_name', 'N/A')}</b><br/>"
            f"Trading Name: {client.get('trading_name', 'N/A')}<br/>"
            f"{client.get('reg_vat', '')}<br/>"
            f"<b>Reg Address:</b> {client.get('reg_address', 'N/A')}<br/>"
            f"<b>Delivery Addr:</b> {client.get('del_address', 'N/A')}",
            style_supplier
        )
    ]]
    client_table = Table(client_box_data, colWidths=[547])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 3))

    # 3. Meta Data Table (Including Live US$/ZAR Exchange Rate Block)
    ex_rate_display = invoice_data.get("exchange_rate_display", "R 18.25")
    meta_data = [
        [
            Paragraph("INVOICE NO", style_meta_hdr),
            Paragraph("TAX REFERENCE", style_meta_hdr),
            Paragraph("DATE", style_meta_hdr),
            Paragraph("US$/ZAR MARKET RATE", style_meta_hdr),
            Paragraph("VALIDITY", style_meta_hdr)
        ],
        [
            Paragraph(str(invoice_data.get("invoice_num", "")), style_meta_val),
            Paragraph(SUPPLIER_DETAILS["vat_no"], style_meta_val),
            Paragraph(invoice_data.get("invoice_date", datetime.today()).strftime('%d %B %Y'), style_meta_val),
            Paragraph(f"<b>{ex_rate_display}</b>", style_meta_val),
            Paragraph(str(invoice_data.get("validity", "")), style_meta_val)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[92, 90, 95, 180, 90])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 4))

    # 4. Products Table
    shipping_mode = str(invoice_data.get('shipping_mode', ''))
    story.append(Paragraph(f"<b>1. COMMERCIAL LINE-ITEM SPECIFICATION ({shipping_mode.upper()} MOQ RUN)</b>", ParagraphStyle('SubT', parent=normal, fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#475569'))))
    story.append(Spacer(1, 2))

    item_table_data = [[
        Paragraph("Bespoke Product Description", ParagraphStyle('IH1', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke)),
        Paragraph("Qty", ParagraphStyle('IH2', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=1)),
        Paragraph("Unit Price<br/>(Excl. VAT)", ParagraphStyle('IH3', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=2)),
        Paragraph("Net Subtotal<br/>(Excl. VAT)", ParagraphStyle('IH4', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=2)),
        Paragraph("Total Price<br/>(Incl. VAT)", ParagraphStyle('IH5', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=2))
    ]]

    products = invoice_data.get("products", [])
    total_qty = 0
    grand_excl = 0.0
    grand_incl = 0.0

    for p in products:
        qty = p["Qty"]
        total_qty += qty
        grand_excl += p["Net Subtotal (Excl)"]
        grand_incl += p["Total Price (Incl)"]

        desc_p = Paragraph(f"<b>{p['SKU']}</b><br/><font color='#475569'>{p['Description']}</font>", style_cell)
        item_table_data.append([
            desc_p,
            Paragraph(f"{qty:,}", ParagraphStyle('C1', parent=style_cell, alignment=1)),
            Paragraph(f"R {p['Unit Price (Excl)']:,.2f}", style_cell_right),
            Paragraph(f"R {p['Net Subtotal (Excl)']:,.2f}", style_cell_right),
            Paragraph(f"R {p['Total Price (Incl)']:,.2f}", style_cell_right)
        ])

    item_table_data.append([
        Paragraph("<b>Combined Program Totals (MOQ Run)</b>", style_cell_bold),
        Paragraph(f"<b>{total_qty:,}</b>", ParagraphStyle('C2', parent=style_cell_bold, alignment=1)),
        Paragraph("", style_cell),
        Paragraph(f"<b>R {grand_excl:,.2f}</b>", style_cell_right_bold),
        Paragraph(f"<b>R {grand_incl:,.2f}</b>", style_cell_right_bold)
    ])

    item_table = Table(item_table_data, colWidths=[237, 50, 80, 90, 90])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F8FAFC')),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 4))

    # 5. Milestone Payment Schedule
    tranche1_excl = grand_excl * 0.50
    tranche1_incl = grand_incl * 0.50

    story.append(Paragraph("<b>2. CONTRACTUAL MILESTONE PAYMENT SCHEDULE</b>", ParagraphStyle('SubT2', parent=normal, fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#475569'))))
    story.append(Spacer(1, 2))

    m_data = [
        [
            Paragraph("Payment Milestone Tranche", ParagraphStyle('MH1', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke)),
            Paragraph("Share %", ParagraphStyle('MH2', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=1)),
            Paragraph("Net Value<br/>(Excl. VAT)", ParagraphStyle('MH3', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=2)),
            Paragraph("Grand Total<br/>(Incl. VAT)", ParagraphStyle('MH4', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=2))
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
    m_table = Table(m_data, colWidths=[277, 50, 110, 110])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 3))

    # 6. Deposit Highlight Box with Payment & FX Terms
    words_str = number_to_words_rand(tranche1_incl)
    deposit_box_data = [[
        Paragraph(
            f"<font size=6 color='#B91C1C'><b>TOTAL AMOUNT NOW DUE TO INITIATE MANUFACTURING (TRANCHE 1 DEPOSIT)</b></font><br/>"
            f"<font size=5.5 color='#475569'>({words_str})</font><br/>"
            f"<font size=10 color='#B91C1C'><b>R {tranche1_incl:,.2f}</b></font><br/>"
            f"<font size=5.5 color='#1E293B'><b>Payment & Foreign Exchange Terms:</b> The 50% initial startup deposit (Tranche 1: R {tranche1_incl:,.2f} Incl. VAT) is absorbed and locked at current pricing upon payment. The remaining 50% balance (Tranche 2) will be adjusted based on the active foreign exchange (FX) rate at the time of final port release payment.</font>",
            ParagraphStyle('DepStyle', parent=normal, alignment=1, leading=8)
        )
    ]]
    dep_table = Table(deposit_box_data, colWidths=[547])
    dep_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#FCA5A5')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(dep_table)
    story.append(Spacer(1, 3))

    # 7. Dual Banking Info
    b1 = invoice_data.get("bank_details_primary", {})
    b2 = invoice_data.get("bank_details_secondary", {})

    bank_hdr_style = ParagraphStyle('BH', parent=normal, fontName='Helvetica-Bold', fontSize=6, textColor=colors.whitesmoke, alignment=1)
    bank_body_style = ParagraphStyle('BC', parent=normal, fontName='Helvetica', fontSize=6, leading=7.5, textColor=colors.HexColor('#1E293B'))

    bank_table_data = [
        [
            Paragraph("<b>OFFICIAL CORPORATE ACCOUNT (FNB 1)</b>", bank_hdr_style),
            Paragraph("<b>FRANCHISE BUSINESS ACCOUNT (FNB 2)</b>", bank_hdr_style)
        ],
        [
            Paragraph(
                f"<b>Account Name:</b> {b1.get('acc_name', '')}<br/>"
                f"<b>Bank:</b> {b1.get('bank_name', '')}<br/>"
                f"<b>Account Type:</b> {b1.get('account_type', '')}<br/>"
                f"<b>Account No:</b> <b>{b1.get('account_number', '')}</b><br/>"
                f"<b>Branch Code:</b> {b1.get('branch_code', '')}",
                bank_body_style
            ),
            Paragraph(
                f"<b>Account Name:</b> {b2.get('acc_name', '')}<br/>"
                f"<b>Bank:</b> {b2.get('bank_name', '')}<br/>"
                f"<b>Account Type:</b> {b2.get('account_type', '')}<br/>"
                f"<b>Account No:</b> <b>{b2.get('account_number', '')}</b><br/>"
                f"<b>Branch Code:</b> {b2.get('branch_code', '')} &nbsp;|&nbsp; <b>SWIFT:</b> {b2.get('swift_code', '')}",
                bank_body_style
            )
        ]
    ]
    bank_table = Table(bank_table_data, colWidths=[273, 274])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(bank_table)
    story.append(Spacer(1, 3))

    # 8. Statutory Compliance & Logistical Clauses
    terms_hdr_style = ParagraphStyle('TH', parent=normal, fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.HexColor('#0F172A'))
    terms_body_style = ParagraphStyle('TB', parent=normal, fontName='Helvetica', fontSize=5.5, leading=7, textColor=colors.HexColor('#334155'))

    terms_data = [
        [
            Paragraph("<b>3. STATUTORY COMPLIANCE & LOGISTICAL CLAUSES</b>", terms_hdr_style)
        ],
        [
            Paragraph(
                "• <b>Raw Material Securement:</b> Production planning, custom material blending, and machine line configurations will trigger automatically upon formal reflection of the 50% Tranche 1 deposit inside our corporate banking treasury. The 50% initial startup pricing is absorbed and fixed as billed.<br/>"
                "• <b>Origin Loading Protection & FX Adjustment:</b> The final 50% balance tranche is contractually tied to origin quality control (QC) verification prior to container loading in China. The final balance payment will be calculated based on the prevailing foreign exchange (FX) rate at the time of transaction settlement.",
                terms_body_style
            )
        ]
    ]
    terms_table = Table(terms_data, colWidths=[547])
    terms_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(terms_table)

    try:
        doc.build(story, onFirstPage=draw_watermark, onLaterPages=draw_watermark)
    except Exception as build_error:
        logger.error(f"Single-page PDF rendering failed: {build_error}. Retrying without single-page enforcement.")
        if enforce_single_page:
            return build_pdf_document(invoice_data, enforce_single_page=False)
        else:
            raise build_error

    buffer.seek(0)
    return buffer
