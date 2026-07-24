# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2017-19 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0
from datetime import date

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestMembershipVariablePeriod(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Membership product with variable period",
                "membership": True,
                "membership_type": "variable",
                "membership_interval_qty": 1,
                "membership_interval_unit": "weeks",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.partner_a = cls.partner  # Set the partner to use on the invoice

    def test_create_invoice_membership_product_days(self):
        self.product.membership_interval_unit = "days"
        self.product.membership_interval_qty = 20
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, invoice_date="2015-07-01"
        )
        membership_line = invoice.invoice_line_ids.membership_line_ids
        membership_line.write({"state": "invoiced"})
        self.assertEqual(
            membership_line.date_from, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(membership_line.date_to, fields.Date.from_string("2015-07-20"))
        self.assertEqual(
            self.partner.membership_start, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            self.partner.membership_stop, fields.Date.from_string("2015-07-20")
        )

    def test_create_invoice_membership_product_week(self):
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, invoice_date="2015-07-01"
        )
        membership_line = invoice.invoice_line_ids.membership_line_ids
        membership_line.write({"state": "invoiced"})
        self.assertEqual(
            membership_line.date_from, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(membership_line.date_to, fields.Date.from_string("2015-07-07"))
        self.assertEqual(
            self.partner.membership_start, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            self.partner.membership_stop, fields.Date.from_string("2015-07-07")
        )

    def test_create_invoice_membership_product_month(self):
        self.product.membership_interval_unit = "months"
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, invoice_date="2015-04-15"
        )
        membership_line = invoice.invoice_line_ids.membership_line_ids
        membership_line.write({"state": "invoiced"})
        self.assertEqual(
            membership_line.date_from, fields.Date.from_string("2015-04-15")
        )
        self.assertEqual(membership_line.date_to, fields.Date.from_string("2015-05-14"))
        self.assertEqual(
            self.partner.membership_start, fields.Date.from_string("2015-04-15")
        )
        self.assertEqual(
            self.partner.membership_stop, fields.Date.from_string("2015-05-14")
        )

    def test_create_invoice_membership_product_year(self):
        self.product.membership_interval_unit = "years"
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, invoice_date="2016-07-01"
        )  # It's leap year
        membership_line = invoice.invoice_line_ids.membership_line_ids
        membership_line.write({"state": "invoiced"})
        self.assertEqual(
            membership_line.date_from, fields.Date.from_string("2016-07-01")
        )
        self.assertEqual(membership_line.date_to, fields.Date.from_string("2017-06-30"))
        self.assertEqual(
            self.partner.membership_start, fields.Date.from_string("2016-07-01")
        )
        self.assertEqual(
            self.partner.membership_stop, fields.Date.from_string("2017-06-30")
        )

    def test_create_invoice_membership_product_year_several(self):
        self.product.membership_interval_unit = "years"
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, quantity=3.0, invoice_date="2015-07-01"
        )
        membership_line_ids = invoice.invoice_line_ids.membership_line_ids
        membership_line_ids.write({"state": "invoiced"})
        self.assertEqual(len(membership_line_ids), 1)
        self.assertEqual(
            membership_line_ids.date_from, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            membership_line_ids.date_to, fields.Date.from_string("2018-06-30")
        )
        self.assertEqual(
            self.partner.membership_start, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            self.partner.membership_stop, fields.Date.from_string("2018-06-30")
        )

    def test_modify_invoice_membership_product(self):
        self.product.membership_interval_unit = "years"
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, quantity=2.0, invoice_date="2015-07-01"
        )
        membership_line_ids = invoice.invoice_line_ids.membership_line_ids
        membership_line_ids.write({"state": "invoiced"})
        self.assertEqual(len(membership_line_ids), 1)
        self.assertEqual(
            membership_line_ids.date_from, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            membership_line_ids.date_to, fields.Date.from_string("2017-06-30")
        )
        self.assertEqual(
            self.partner.membership_start, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            self.partner.membership_stop, fields.Date.from_string("2017-06-30")
        )
        # Remove quantity
        invoice.invoice_line_ids.quantity = 1.0
        membership_line_ids = invoice.invoice_line_ids.membership_line_ids
        self.assertEqual(len(membership_line_ids), 1)
        self.assertEqual(
            membership_line_ids.date_from, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            membership_line_ids.date_to, fields.Date.from_string("2016-06-30")
        )

    def test_modify_invoice_membership_product_type(self):
        self.product.membership = False
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, invoice_date="2015-07-01"
        )
        self.assertFalse(invoice.invoice_line_ids.membership_line_ids)
        self.product.membership = True
        invoice.invoice_line_ids.quantity = 1.0
        self.assertEqual(len(invoice.invoice_line_ids.membership_line_ids), 1)

    def test_create_and_modify_invoice_line_membership_product(self):
        self.product.membership_interval_qty = 20
        self.product.membership_interval_unit = "days"
        invoice = self._create_invoice_one_line(
            product_id=self.product.id, invoice_date="2015-07-01"
        )
        membership_line = invoice.invoice_line_ids.membership_line_ids
        membership_line.write({"state": "invoiced"})
        self.assertEqual(
            membership_line.date_from, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(membership_line.date_to, fields.Date.from_string("2015-07-20"))
        self.assertEqual(
            self.partner.membership_start, fields.Date.from_string("2015-07-01")
        )
        self.assertEqual(
            self.partner.membership_stop, fields.Date.from_string("2015-07-20")
        )

    def test_check_membership_expiry(self):
        self.env["membership.membership_line"].create(
            {
                "partner_id": self.partner.id,
                "membership_id": self.product.id,
                "member_price": 1.0,
                "date": "2014-01-01",
                "date_from": "2014-01-01",
                "date_to": "2014-12-31",
                "state": "paid",
            }
        )
        # Force state to let the calculation return to the computed one
        free_state = self.partner.free_member
        self.partner.write({"free_member": not free_state})
        self.partner.write({"free_member": free_state})
        self.env["res.partner"].check_membership_expiry()
        self.assertEqual(self.partner.membership_state, "old")

    def test_get_next_date(self):
        test_suite = [
            # Add here more border cases that can be detected in the future
            ("2015-01-01", "days", 25, date(day=26, month=1, year=2015)),
            ("2015-01-01", "weeks", 1, date(day=8, month=1, year=2015)),
            ("2015-01-01", "months", 3, date(day=1, month=4, year=2015)),
            ("2015-01-01", "years", 1, date(day=1, month=1, year=2016)),
        ]
        template_model = self.env["product.template"]
        for old_date, interval, qty, next_date in test_suite:
            template = template_model.new()
            template.membership_type = "variable"
            template.membership_interval_unit = interval
            template.membership_interval_qty = qty
            self.assertEqual(template._get_next_date(old_date), next_date)

    def test_create_invoice_line_with_no_product(self):
        invoice = self._create_invoice_one_line(
            product_id=None, price_unit=100.0, invoice_date="2015-07-01"
        )
        self.assertFalse(invoice.invoice_line_ids.product_id)
        self.assertFalse(invoice.invoice_line_ids.membership_line_ids)
