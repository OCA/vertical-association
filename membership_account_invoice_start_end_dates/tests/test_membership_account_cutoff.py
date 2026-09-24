# Copyright 2016-2020 Akretion France (http://www.akretion.com/)
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License LGPL-3 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date

from odoo import exceptions
from odoo.tests.common import TransactionCase, freeze_time


@freeze_time("2026-01-01 09:00:00")
class TestMembershipAccountCutoff(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.member = cls.env["res.partner"].create({"name": "In-between member"})
        cls.date_from = date(2026, 1, 1)
        cls.date_to = date(2026, 12, 31)
        cls.product = cls.env["product.product"].create(
            [
                {
                    "name": "Membership",
                    "membership": True,
                    "membership_date_from": cls.date_from,
                    "membership_date_to": cls.date_to,
                }
            ]
        )
        cls.member.create_membership_invoice(
            product=cls.product,
            amount=10.0,
        )
        cls.member_line = cls.member.member_lines
        cls.invoice_line = cls.member_line.account_invoice_line
        cls.invoice = cls.invoice_line.move_id

    def test_invoice_dates(self):
        self.assertEqual(self.invoice_line.start_date, self.member_line.date_from)
        self.assertEqual(self.invoice_line.end_date, self.member_line.date_to)

    def test_invoice_change_dates(self):
        new_date = date(2026, 2, 2)
        self.invoice_line.start_date = new_date
        self.assertEqual(self.member_line.date_from, new_date)

    def test_membership_change_dates(self):
        new_date = date(2026, 3, 3)
        self.member_line.date_to = new_date
        self.assertEqual(self.invoice_line.end_date, new_date)

    def test_constrain_membership_change_dates(self):
        """Test constrain preventing membership date changes when the
        invoice is already posted"""
        self.invoice.action_post()
        with self.assertRaises(exceptions.ValidationError):
            self.member_line.date_to = date(2026, 3, 3)

    def test_constrain_invoice_multiple_memberships(self):
        """Test constrain preventing multiple membership lines for one
        invoice line"""
        with self.assertRaises(exceptions.ValidationError):
            self.env["membership.membership_line"].create(
                [
                    {
                        "partner": self.member.id,
                        "membership_id": self.product.id,
                        "date_from": self.date_from,
                        "date_to": self.date_to,
                        "member_price": 10.0,
                        "account_invoice_line": self.invoice_line.id,
                    }
                ]
            )
