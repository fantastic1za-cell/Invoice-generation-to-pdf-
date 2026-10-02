"""
Core Configuration and Immutable System Constants
"""
import os
from typing import Dict, Any

APP_TITLE = "MR MOBILE SA - Pro Forma Generator"
APP_ICON = "📄"

# ---------------------------------------------------------
# IMMUTABLE CONSTANTS (NON-EDITABLE HARDCODED VALUES)
# ---------------------------------------------------------
SUPPLIER_DETAILS: Dict[str, Any] = {
    "company": "IRESQ LA LUCIA PTY LTD",
    "trading": "MR MOBILE SA",
    "vat_no": "4960281899",
    "email": "nisaar@fantastic1.com",
    "address": "58 Paarlshoop Road, Homestead Park, 2092 Johannesburg, South Africa",
    "contact": "068 710 1939 / 082 786 7712"
}

BANK_DETAILS_PRIMARY: Dict[str, Any] = {
    "title": "PRIMARY CORPORATE ACCOUNT",
    "acc_name": "IRESQ LA LUCIA PTY LTD",
    "bank_name": "First National Bank (FNB)",
    "account_type": "First Business Zero",
    "account_number": "63152083390",
    "branch_code": "256505 (Melville)"
}

BANK_DETAILS_SECONDARY: Dict[str, Any] = {
    "title": "FRANCHISE BUSINESS ACCOUNT (FBA)",
    "acc_name": "IRESQ LA LUCIA PTY LTD T/A MMSA FBA",
    "bank_name": "First National Bank (FNB)",
    "account_type": "Franchise Business Account",
    "account_number": "63230107658",
    "branch_code": "25535",
    "swift_code": "FIRNZAJJ"
}

PRESET_CLIENTS: Dict[str, Dict[str, str]] = {
    "Twenty-Five Star (Pty) Ltd (Pedros DBN)": {
        "client_name": "Twenty-Five Star (Pty) Ltd",
        "trading_name": "Pedros Distribution Centre DBN",
        "reg_vat": "Co. Reg: 2022/686760/07 | VAT: 4690317583",
        "reg_address": "33 Aiken Street, Port Shepstone, KZN, 4240",
        "del_address": "4-6 Suzuka Road, Westmead, Pinetown, 3608"
    }
}

DEFAULT_FALLBACK_CLIENT = {
    "client_name": "Client Name Pending",
    "trading_name": "N/A",
    "reg_vat": "VAT: Pending",
    "reg_address": "Address Not Provided",
    "del_address": "Address Not Provided"
}
