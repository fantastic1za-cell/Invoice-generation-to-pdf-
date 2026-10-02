"""
Streamlit UI Controller with Failsafe Exception Handling
"""
import streamlit as st
import pandas as pd
from datetime import datetime

import config
from helpers import safe_float_convert, safe_int_convert, calculate_line_item
from pdf_engine import build_pdf_document

st.set_page_config(page_title=config.APP_TITLE, page_icon=config.APP_ICON, layout="wide")

# Safe Execution Wrapper for UI
def main():
    try:
        st.title("📄 Pro Forma Tax Invoice Generator")
        st.caption(
            f"Supplier: **{config.SUPPLIER_DETAILS['company']} t/a {config.SUPPLIER_DETAILS['trading']}** | "
            f"Locked VAT: **{config.SUPPLIER_DETAILS['vat_no']}** | "
            f"Locked Email: **{config.SUPPLIER_DETAILS['email']}**"
        )

        # Section 1: Metadata
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
            st.text_input("Tax Reference / VAT (Locked)", config.SUPPLIER_DETAILS["vat_no"], disabled=True)
        with col4:
            st.info(
                f"🔒 **Primary Acc:** {config.BANK_DETAILS_PRIMARY['account_number']}\n\n"
                f"🔒 **Secondary Acc:** {config.BANK_DETAILS_SECONDARY['account_number']}"
            )

        st.markdown("---")

        # Section 2: Client
        st.header("2. Client & Billing Details")
        client_option = st.radio("Client Details Source:", ["Existing Client (Preset)", "New Client Entry"], horizontal=True)

        if client_option == "Existing Client (Preset)":
            selected_preset = st.selectbox("Select Preset Client:", list(config.PRESET_CLIENTS.keys()))
            client_data = config.PRESET_CLIENTS.get(selected_preset, config.DEFAULT_FALLBACK_CLIENT)
        else:
            client_data = {
                "client_name": st.text_input("Client Legal Name", placeholder="e.g. Twenty-Five Star (Pty) Ltd"),
                "trading_name": st.text_input("Trading Name", placeholder="e.g. Pedros Distribution Centre DBN"),
                "reg_vat": st.text_input("Co. Reg & VAT", placeholder="Co. Reg: 2022/686760/07 | VAT: 4690317583"),
                "reg_address": st.text_area("Registered Address", placeholder="33 Aiken Street, Port Shepstone, KZN, 4240", height=70),
                "del_address": st.text_area("Delivery Address", placeholder="4-6 Suzuka Road, Westmead, Pinetown, 3608", height=70)
            }

        st.markdown("---")

        # Section 3: Dynamic Products
        st.header("3. Commercial Line-Item Specification")
        num_products = st.number_input("How many products / line items?", min_value=1, max_value=10, value=1, step=1)

        products = []
        for i in range(safe_int_convert(num_products, 1)):
            st.subheader(f"Item #{i+1}")
            p1, p2 = st.columns([1, 3])
            with p1:
                sku = st.text_input(f"SKU / Item Code #{i+1}", value="600ml Food Flask" if i == 0 else f"ITEM-00{i+1}", key=f"sku_{i}")
            with p2:
                desc = st.text_input(f"Bespoke Description #{i+1}", value="Plain SS304 Body Configuration. Landed DDP Pinetown." if i == 0 else "", key=f"desc_{i}")
            
            q1, q2 = st.columns(2)
            with q1:
                raw_qty = st.number_input(f"Quantity (Units) #{i+1}", min_value=1, value=3000 if i == 0 else 1, step=1, key=f"qty_{i}")
                qty = safe_int_convert(raw_qty, 1)
            with q2:
                raw_price = st.number_input(f"Unit Price Excl. VAT (R) #{i+1}", min_value=0.0, value=155.32 if i == 0 else 0.0, step=0.01, format="%.2f", key=f"price_{i}")
                unit_price = safe_float_convert(raw_price, 0.0)
            
            calcs = calculate_line_item(qty, unit_price)
            
            products.append({
                "SKU": sku,
                "Description": desc,
                "Qty": qty,
                "Unit Price (Excl)": unit_price,
                "Net Subtotal (Excl)": calcs["subtotal_excl"],
                "VAT (15%)": calcs["vat_amount"],
                "Total Price (Incl)": calcs["total_incl"]
            })

        st.markdown("---")

        # Section 4: Calculations & Summary
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
        tranche1_incl = grand_incl * 0.50

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Net Program Subtotal (Excl)", f"R {grand_excl:,.2f}")
        c2.metric("Total VAT (15%)", f"R {grand_vat:,.2f}")
        c3.metric("Grand Total (Incl. VAT)", f"R {grand_incl:,.2f}")
        c4.metric("TRANCHE 1 DEPOSIT (50%)", f"R {tranche1_incl:,.2f}")

        st.markdown("---")

        # Section 5: Secure Export
        invoice_payload = {
            "invoice_date": invoice_date,
            "invoice_num": invoice_num,
            "shipping_mode": shipping_mode,
            "due_date": due_date_str,
            "validity": validity_str,
            "client": client_data,
            "products": products
        }

        # Safe PDF Render Call
        try:
            pdf_buffer = build_pdf_document(invoice_payload, enforce_single_page=True)
            st.download_button(
                label="📥 Download Pro Forma PDF (A4 Single Page)",
                data=pdf_buffer,
                file_name=f"Pro_Forma_Invoice_{invoice_num}_{client_data.get('client_name', 'Client').replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as pdf_err:
            st.error("An error occurred while compiling the PDF. Attempting standard engine recovery...")
            config.logger.error(f"Primary PDF compile error: {pdf_err}")

    except Exception as app_err:
        st.critical("A system error occurred. Application isolated safely.")
        st.exception(app_err)

if __name__ == "__main__":
    main()
