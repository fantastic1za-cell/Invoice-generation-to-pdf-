# ==============================================================================
# SCRIPT MODULE : config.py
# REPOSITORY    : fantastic1za-cell/Invoice-generator-3
# AUTHOR        : Nisaar Ally
# TIMESTAMP     : 2026-10-04 11:45:00 SAST
# LOCKED BY     : Nisaar Ally
# STATUS        : PRODUCTION LOCKED (SARS-Compliant Engine)
# ==============================================================================

import os

# Company Branding & Identity
COMPANY_NAME = "IRESQ LA LUCIA PTY LTD"
TRADING_NAME = "MR MOBILE SA"
REGISTRATION_NUMBER = "2020/123456/07"
VAT_NUMBER = "4960281899"
SUPPLIER_ADDRESS = "58 Paarlshoop Road, Homestead Park, 2092, Johannesburg, South Africa"
CONTACT_EMAIL = "nisaar@fantastic1.com"

# SMTP Relay Infrastructure & Redundancy Defaults
SMTP_SERVER = "smtp.gmail.com"
SMTP_PRIMARY_PORT = 465   # SSL
SMTP_FALLBACK_PORT = 587  # STARTTLS
SMTP_SENDER = "fantastic1za@gmail.com"
SMTP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "khvo hsun zjpe vcqf")

# Dual Banking Configurations (FNB 1 & FNB 2 with SWIFT Codes)
BANKING_DETAILS = {
    "PRIMARY_ACCOUNT": {
        "title": "OFFICIAL CORPORATE ACCOUNT (FNB 1)",
        "account_name": "IRESQ LA LUCIA PTY LTD",
        "bank": "First National Bank (FNB)",
        "account_type": "Current Account",
        "account_number": "63152083390",
        "branch_code": "256505 (Melville)",
        "swift_code": "FIRNZAJJ"
    },
    "SECONDARY_ACCOUNT": {
        "title": "FRANCHISE BUSINESS ACCOUNT (FNB 2)",
        "account_name": "IRESQ LA LUCIA PTY LTD T/A MMSA FBA",
        "bank": "First National Bank (FNB)",
        "account_type": "Franchise Business Account",
        "account_number": "63230107658",
        "branch_code": "256505",
        "swift_code": "FIRNZAJJ"
    }
}

# Statutory Compliance Clauses
STATUTORY_CLAUSES = [
    "Raw Material Securement: Production planning, custom material blending, and machine line configurations will trigger automatically upon formal reflection of the 50% deposit inside our corporate banking treasury. The 50% initial startup pricing is absorbed and fixed as billed.",
    "Origin Loading Protection & FX Adjustment: The final 50% balance tranche is contractually tied to origin quality control (QC) verification prior to container loading in China. The final balance payment will be calculated based on the prevailing foreign exchange (FX) rate at the time of transaction settlement."
]

LOGO_PATH = "mmsalogo.png.jpg"
CURRENCY_SYMBOL = "R"
TAX_RATE = 0.15
