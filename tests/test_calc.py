import unittest
from decimal import Decimal as Dm
from core.calculation import LineItem, Adjustments, calculate, CalculationError
from core.formatting import format_amount


class CalcTests(unittest.TestCase):
    def test_spec_example(self):
        t = calculate([LineItem("1", "10000")],
                      Adjustments(discount_type="percent", discount_value="10", vat_percent="5", delivery="100"))
        self.assertEqual(t.overall_discount, Dm("1000.00"))
        self.assertEqual(t.vat, Dm("450.00"))
        self.assertEqual(t.grand_total, Dm("9550.00"))

    def test_vat_before_discount(self):
        t = calculate([LineItem("1", "10000")],
                      Adjustments(discount_value="10", vat_percent="5", vat_mode="before_discount"))
        self.assertEqual(t.vat, Dm("500.00"))
        self.assertEqual(t.grand_total, Dm("9500.00"))

    def test_decimal_safety(self):
        self.assertEqual(calculate([LineItem("3", "0.10")]).subtotal, Dm("0.30"))

    def test_item_discounts(self):
        t = calculate([LineItem("2", "500", "percent", "10"), LineItem("1", "300", "fixed", "50")])
        self.assertEqual(t.subtotal, Dm("1150.00"))
        self.assertEqual(t.item_discount_total, Dm("150.00"))

    def test_fixed_discount_capped(self):
        self.assertEqual(calculate([LineItem("1", "100", "fixed", "999")]).subtotal, Dm("0.00"))

    def test_rounding_and_due(self):
        t = calculate([LineItem("1", "100.60")], Adjustments(rounding="nearest", paid="50", previous_due="20"))
        self.assertEqual(t.grand_total, Dm("101"))
        self.assertEqual(t.rounding_adjustment, Dm("0.40"))
        self.assertEqual(t.current_due, Dm("71"))

    def test_overpay_change(self):
        t = calculate([LineItem("1", "100")], Adjustments(paid="150"))
        self.assertEqual(t.change_due, Dm("50")); self.assertEqual(t.current_due, 0)

    def test_validation(self):
        with self.assertRaises(CalculationError): LineItem("-1", "10")
        with self.assertRaises(CalculationError): LineItem("1", "-10")
        with self.assertRaises(CalculationError): Adjustments(discount_value="101")
        with self.assertRaises(TypeError): LineItem(1.5, "10")

    def test_formatting(self):
        self.assertEqual(format_amount("100000"), "1,00,000.00")
        self.assertEqual(format_amount("12345678.5"), "1,23,45,678.50")
        self.assertEqual(format_amount("1250", bangla=True, symbol=True), "৳১,২৫০.০০")


if __name__ == "__main__":
    unittest.main()
