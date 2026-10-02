"""
Helper Utilities, Calculation Logic, and Data Fallbacks
"""
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentGenerator")

def safe_float_convert(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse float for '{value}'. Defaulting to {default}. Error: {e}")
        return default

def safe_int_convert(value: Any, default: int = 1) -> int:
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse int for '{value}'. Defaulting to {default}. Error: {e}")
        return default

def calculate_line_item(qty: int, unit_price: float, vat_rate: float = 0.15) -> Dict[str, float]:
    qty = max(1, qty)
    unit_price = max(0.0, unit_price)
    
    subtotal_excl = round(qty * unit_price, 2)
    vat_amount = round(subtotal_excl * vat_rate, 2)
    total_incl = round(subtotal_excl + vat_amount, 2)
    
    return {
        "subtotal_excl": subtotal_excl,
        "vat_amount": vat_amount,
        "total_incl": total_incl
    }

def number_to_words_rand(amount: float) -> str:
    try:
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
                 "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def _convert_nn(n):
            if n < 20: return units[n]
            for i, t in enumerate(tens):
                if i >= 2 and n < (i + 1) * 10:
                    rest = units[n - i * 10]
                    return f"{t}-{rest}" if rest else t
            return ""

        def _convert_nnn(n):
            word = ""
            rem = n % 100
            hundreds = n // 100
            if hundreds > 0:
                word = f"{units[hundreds]} Hundred"
                if rem > 0: word += f" and {_convert_nn(rem)}"
            else:
                word = _convert_nn(rem)
            return word

        int_val = int(round(amount))
        if int_val == 0: return "Zero Rand"
        
        thousands = (int_val // 1000) % 1000
        millions = (int_val // 1000000) % 1000
        hundreds = int_val % 1000
        
        res = []
        if millions: res.append(f"{_convert_nnn(millions)} Million")
        if thousands: res.append(f"{_convert_nnn(thousands)} Thousand")
        if hundreds: res.append(f"{_convert_nnn(hundreds)}")
        
        return " ".join(res) + " Rand, Inclusive of 15% Local Sales VAT"
    except Exception as e:
        logger.error(f"Error executing number_to_words_rand: {e}")
        return f"R {amount:,.2f} Inclusive of VAT"
