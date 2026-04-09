"""
CineStats — Currency Converter
Section 3.3 of the v1.0 specification.

Rules:
  - Worldwide Gross: always USD primary. Non-USD selected → converted in brackets.
  - India Figures: always INR (₹ Cr) primary. Converted in brackets if non-INR.
  - 1 Crore = 10,000,000 INR
"""
from typing import Optional
from constants import CURRENCY_SYMBOLS, FALLBACK_RATES

# 1 Crore = 10 million INR
CRORE = 10_000_000


def convert(amount: float, from_currency: str, to_currency: str,
            rates: dict) -> float:
    """Convert an amount between currencies.

    Args:
        amount: the amount in from_currency
        from_currency: source currency code (e.g. 'USD')
        to_currency: target currency code (e.g. 'INR')
        rates: dict mapping currency code → rate (USD-based)

    Returns:
        Converted amount in to_currency.
    """
    if from_currency == to_currency:
        return amount
    if not amount:
        return 0.0

    from_rate = rates.get(from_currency, FALLBACK_RATES.get(from_currency, 1.0))
    to_rate = rates.get(to_currency, FALLBACK_RATES.get(to_currency, 1.0))

    # Convert via USD as base
    usd_amount = amount / from_rate
    return usd_amount * to_rate


def usd_to_crore(usd_amount: float, rates: dict) -> float:
    """Convert USD to Indian Crores."""
    inr = convert(usd_amount, "USD", "INR", rates)
    return inr / CRORE


def crore_to_usd(crore_amount: float, rates: dict) -> float:
    """Convert Indian Crores to USD."""
    inr = crore_amount * CRORE
    return convert(inr, "INR", "USD", rates)


def format_money(amount: float, currency: str, compact: bool = True) -> str:
    """Format a monetary amount with currency symbol.

    Args:
        amount: amount in the given currency
        currency: currency code
        compact: if True, use M/B/K suffixes for large numbers
    """
    if amount is None:
        return "N/A"

    symbol = CURRENCY_SYMBOLS.get(currency, currency)

    if compact:
        abs_amount = abs(amount)
        if abs_amount >= 1_000_000_000:
            return f"{symbol}{amount/1e9:.1f}B"
        elif abs_amount >= 1_000_000:
            return f"{symbol}{amount/1e6:.1f}M"
        elif abs_amount >= 1_000:
            return f"{symbol}{amount/1e3:.0f}K"

    return f"{symbol}{amount:,.0f}"


def format_crore(amount: float) -> str:
    """Format INR Crores with the rupee symbol."""
    if amount is None:
        return "N/A"
    return f"₹{amount:.2f} Cr"


def format_with_conversion(primary_amount: float, primary_currency: str,
                           target_currency: str, rates: dict,
                           primary_is_crore: bool = False) -> str:
    """Format a primary amount with an optional converted bracket.

    Rules from Section 3.3:
      - If primary_currency == target_currency → just show primary.
      - Otherwise → 'primary (converted_value)'.

    Args:
        primary_amount: amount in primary currency
        primary_currency: 'USD' or 'INR'
        target_currency: selected display currency
        rates: exchange rates dict
        primary_is_crore: if True, primary_amount is in Crores
    """
    if primary_amount is None:
        return "N/A"

    if primary_is_crore:
        primary_str = format_crore(primary_amount)
        if target_currency == "INR":
            return primary_str
        # Convert crores to target currency
        inr = primary_amount * CRORE
        converted = convert(inr, "INR", target_currency, rates)
        return f"{primary_str} ({format_money(converted, target_currency)})"
    else:
        primary_str = format_money(primary_amount, primary_currency)
        if primary_currency == target_currency:
            return primary_str
        converted = convert(primary_amount, primary_currency, target_currency, rates)
        return f"{primary_str} ({format_money(converted, target_currency)})"
