# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import date
from unittest.mock import patch

from odoo.tests import Form, common

from odoo.addons.membership_prorate.models.account_move_line import AccountMoveLine


class TestMembershipProrate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Membership product with prorate",
                "membership": True,
                "membership_prorate": True,
                "membership_date_from": "2017-01-01",
                "membership_date_to": "2017-12-31",
            }
        )
        receivable = cls.env["account.account"].create(
            {
                "name": "Test receivable account",
                "code": "TESTRA",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test",
                "property_account_receivable_id": receivable.id,
            }
        )

    def test_create_invoice_membership_product_wo_prorate(self):
        self.product.membership_prorate = False
        invoice = self.partner.create_membership_invoice(self.product, 1.0)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, 1.0)

    def test_create_invoice_membership_product_prorate(self):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = self.partner
        invoice_form.invoice_date = date(2017, 7, 1)
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.price_unit = 100.0
            line_form.tax_ids.clear()
        invoice = invoice_form.save()
        # Result is rounded to 2 decimals for avoiding the fail in tests
        # if "Product Unit of Measure" precision changes in the future
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.50, 2)
        memb_line = self.env["membership.membership_line"].search(
            [("account_invoice_line", "=", invoice.invoice_line_ids[0].id)], limit=1
        )
        self.assertAlmostEqual(memb_line.member_price, 50.00, 2)
        self.assertEqual(memb_line.date_from, date(2017, 7, 1))
        # Set the date six months before the membership period
        with Form(invoice) as invoice_form:
            invoice_form.invoice_date = date(2016, 7, 1)
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product
                line_form.price_unit = 100.0
                line_form.tax_ids.clear()
        # The whole period is calculated
        self.assertAlmostEqual(invoice.invoice_line_ids[1].quantity, 1.0, 2)
        memb_line = self.env["membership.membership_line"].search(
            [("account_invoice_line", "=", invoice.invoice_line_ids[1].id)], limit=1
        )
        self.assertAlmostEqual(memb_line.member_price, 100.00, 2)
        self.assertEqual(memb_line.date_from, date(2017, 1, 1))
        # Set the date six months after the membership period
        with Form(invoice) as invoice_form:
            invoice_form.invoice_date = date(2018, 7, 1)
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product
                line_form.price_unit = 100.0
                line_form.tax_ids.clear()
        # Nothing to invoice
        self.assertAlmostEqual(invoice.invoice_line_ids[2].quantity, 0, 2)
        memb_line = self.env["membership.membership_line"].search(
            [("account_invoice_line", "=", invoice.invoice_line_ids[2].id)], limit=1
        )
        self.assertAlmostEqual(memb_line.member_price, 0.00, 2)
        self.assertEqual(memb_line.date_from, date(2017, 12, 31))

    def test_create_invoice_membership_product_prorate_variable_period(self):
        """It is a test for case where membership type is set to variable
        on product with membership_prorate_variable_period not installed"""

        def _get_membership_interval(self, product, date):
            return False, False

        with patch.object(
            AccountMoveLine,
            "_get_membership_interval",
            _get_membership_interval,
        ):
            invoice = self.partner.create_membership_invoice(self.product, 1.0)
            self.assertEqual(invoice.invoice_line_ids[0].quantity, 1.0)
