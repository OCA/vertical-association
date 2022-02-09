# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2015 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import datetime

from odoo import exceptions, fields
from odoo.tests import Form, SavepointCase


class TestMembershipProrateVariablePeriod(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Membership product with prorate",
                "membership": True,
                "membership_prorate": True,
                "membership_type": "variable",
                "membership_interval_qty": 1,
                "membership_interval_unit": "weeks",
            }
        )
        receivable_type = cls.env["account.account.type"].create(
            {
                "name": "Test receivable account",
                "type": "receivable",
                "internal_group": "income",
            }
        )
        receivable = cls.env["account.account"].create(
            {
                "name": "Test receivable account",
                "code": "TEST_RA",
                "user_type_id": receivable_type.id,
                "reconcile": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test",
                "property_account_receivable_id": receivable.id,
            }
        )

    def create_invoice(self, invoice_date):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.invoice_date = invoice_date
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
        return invoice_form.save()

    def test_create_invoice_membership_product_wo_prorate(self):
        self.product.membership_prorate = False
        invoice = self.create_invoice(datetime.date.today())
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 1.0, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, "waiting")
        self.assertEqual(self.partner.membership_state, "waiting")

    def test_create_invoice_membership_product_prorate_fixed(self):
        self.product.membership_type = "fixed"
        self.product.membership_date_from = "2017-01-01"
        self.product.membership_date_to = "2017-12-31"
        invoice = self.create_invoice("2017-04-01")
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.75, 2)

    def test_create_invoice_membership_product_prorate_week(self):
        invoice = self.create_invoice("2015-01-01")  # It's thursday
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.43, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, "waiting")
        self.assertEqual(
            self.partner.member_lines[0].date_from,
            fields.Date.from_string("2015-01-01"),
        )
        self.assertEqual(
            self.partner.member_lines[0].date_to, fields.Date.from_string("2015-01-04")
        )

    def test_create_invoice_membership_product_prorate_month(self):
        self.product.membership_interval_unit = "months"
        invoice = self.create_invoice("2015-04-15")
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.5, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, "waiting")
        self.assertEqual(
            self.partner.member_lines[0].date_from,
            fields.Date.from_string("2015-04-15"),
        )
        self.assertEqual(
            self.partner.member_lines[0].date_to, fields.Date.from_string("2015-04-30")
        )

    def test_create_invoice_membership_product_prorate_year(self):
        self.product.membership_interval_unit = "years"
        invoice = self.create_invoice("2016-07-01")
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.5, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, "waiting")
        self.assertEqual(
            self.partner.member_lines[0].date_from,
            fields.Date.from_string("2016-07-01"),
        )
        self.assertEqual(
            self.partner.member_lines[0].date_to, fields.Date.from_string("2016-12-31")
        )

    def test_get_next_date(self):
        # Weeks
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = "weeks"
        date = fields.Date.from_string("2015-07-01")
        self.assertEqual(
            datetime.date(day=6, month=7, year=2015), self.product._get_next_date(date)
        )
        self.assertEqual(
            datetime.date(day=20, month=7, year=2015),
            self.product._get_next_date(date, qty=3),
        )
        self.product.membership_interval_qty = 2
        self.assertEqual(
            datetime.date(day=10, month=8, year=2015),
            self.product._get_next_date(date, qty=3),
        )
        # Months
        date = fields.Date.from_string("2015-07-31")
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = "months"
        self.assertEqual(
            datetime.date(day=1, month=8, year=2015), self.product._get_next_date(date)
        )
        self.assertEqual(
            datetime.date(day=1, month=10, year=2015),
            self.product._get_next_date(date, qty=3),
        )
        self.product.membership_interval_qty = 2
        self.assertEqual(
            datetime.date(day=1, month=3, year=2016),
            self.product._get_next_date(date, qty=4),
        )
        # Years
        date = fields.Date.from_string("2015-07-31")
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = "years"
        self.assertEqual(
            datetime.date(day=1, month=1, year=2016), self.product._get_next_date(date)
        )
        self.assertEqual(
            datetime.date(day=1, month=1, year=2018),
            self.product._get_next_date(date, qty=3),
        )
        self.product.membership_interval_qty = 2
        self.assertEqual(
            datetime.date(day=1, month=1, year=2021),
            self.product._get_next_date(date, qty=3),
        )

    def test_exceptions(self):
        # Test daily period
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = "days"
        with self.assertRaises(exceptions.UserError):
            self.product._get_next_date(fields.Date.from_string("2015-07-01"))
        with self.assertRaises(exceptions.UserError):
            self.create_invoice(fields.Date.today())
