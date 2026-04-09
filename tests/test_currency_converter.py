"""Tests for currency converter."""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.logic.currency_converter import (
    convert, usd_to_crore, crore_to_usd,
    format_money, format_crore, format_with_conversion
)
from constants import FALLBACK_RATES


class TestConvert(unittest.TestCase):

    def test_same_currency(self):
        self.assertEqual(convert(100, "USD", "USD", FALLBACK_RATES), 100)

    def test_usd_to_inr(self):
        result = convert(100, "USD", "INR", FALLBACK_RATES)
        # $100 / 1.0 (USD rate) * 93 (INR rate) = ₹9,300
        self.assertAlmostEqual(result, 100 * 93, places=0)

    def test_inr_to_usd(self):
        result = convert(9300, "INR", "USD", FALLBACK_RATES)
        # ₹9300 / 93 (INR rate) * 1.0 (USD rate) = $100
        self.assertAlmostEqual(result, 100.0, places=0)

    def test_cross_currency(self):
        # EUR → GBP via USD base: 100 EUR / 0.92 * 0.79 = 85.87 GBP
        result = convert(100, "EUR", "GBP", FALLBACK_RATES)
        expected = 100 / 0.86 * 0.75
        self.assertAlmostEqual(result, expected, places=1)

    def test_zero_amount(self):
        self.assertEqual(convert(0, "USD", "INR", FALLBACK_RATES), 0.0)


class TestCreoreConversions(unittest.TestCase):

    def test_usd_to_crore(self):
        result = usd_to_crore(100_000_000, FALLBACK_RATES)
        # $100M × 93 / 10M = 930 Cr
        self.assertAlmostEqual(result, 930.0, places=0)

    def test_crore_to_usd(self):
        result = crore_to_usd(930, FALLBACK_RATES)
        # 930 Cr × 10M INR / 93 = $100M
        self.assertAlmostEqual(result, 100_000_000, delta=1_000_000)


class TestFormatMoney(unittest.TestCase):

    def test_billions(self):
        self.assertEqual(format_money(2_500_000_000, "USD"), "$2.5B")

    def test_millions(self):
        self.assertEqual(format_money(599_000_000, "USD"), "$599.0M")

    def test_thousands(self):
        self.assertEqual(format_money(5000, "USD"), "$5K")

    def test_inr_symbol(self):
        self.assertEqual(format_money(100_000_000, "INR"), "₹100.0M")

    def test_none(self):
        self.assertEqual(format_money(None, "USD"), "N/A")


class TestFormatCrore(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(format_crore(105.5), "₹105.50 Cr")

    def test_none(self):
        self.assertEqual(format_crore(None), "N/A")


class TestFormatWithConversion(unittest.TestCase):

    def test_usd_same_currency(self):
        result = format_with_conversion(599_000_000, "USD", "USD", FALLBACK_RATES)
        self.assertEqual(result, "$599.0M")

    def test_usd_with_inr_conversion(self):
        result = format_with_conversion(599_000_000, "USD", "INR", FALLBACK_RATES)
        self.assertIn("$599.0M", result)
        self.assertIn("₹", result)

    def test_crore_with_usd_conversion(self):
        result = format_with_conversion(105.5, "INR", "USD", FALLBACK_RATES, primary_is_crore=True)
        self.assertIn("₹105.50 Cr", result)
        self.assertIn("$", result)


if __name__ == "__main__":
    unittest.main()
