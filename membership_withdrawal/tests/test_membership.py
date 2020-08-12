# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestMembership(TransactionCase):
    def setUp(self):
        super().setUp()

        self.next_two_months = fields.Date.today() + timedelta(days=60)
        self.next_month = fields.Date.today() + timedelta(days=30)
        self.reason = self.env.ref("membership_withdrawal.reason_unsatisfied")
        self.partner = self.env["res.partner"].create({"name": "Test company"})
        self.child = self.env["res.partner"].create(
            {"name": "Test child", "associate_member": self.partner.id}
        )
        self.product = self.env["product.product"].create(
            {
                "type": "service",
                "name": "Membership 2016",
                "membership": True,
                "membership_date_from": "2016-01-01",
                "membership_date_to": self.next_two_months,
                "list_price": 100.00,
            }
        )

    def test_partner_compute(self):
        line = self.env["membership.membership_line"].create(
            {
                "membership_id": self.product.id,
                "member_price": 100.00,
                "date": "2016-01-15",
                "date_from": "2016-01-01",
                "date_to": self.next_two_months,
                "partner": self.partner.id,
                "state": "invoiced",
            }
        )
        self.assertFalse(self.partner.membership_last_withdrawal_reason_id)
        self.assertFalse(self.partner.membership_last_withdrawal_date)
        self.assertFalse(self.child.membership_last_withdrawal_reason_id)
        self.assertFalse(self.child.membership_last_withdrawal_date)
        line.write(
            {
                "date_withdrawal": "2016-06-07",
                "withdrawal_reason_id": self.reason.id,
                "date_cancel": self.next_month,
            }
        )
        self.assertEqual(
            self.reason.id, self.partner.membership_last_withdrawal_reason_id.id
        )
        self.assertEqual(
            fields.Date.from_string("2016-06-07"),
            self.partner.membership_last_withdrawal_date,
        )
        self.assertEqual(self.next_month, self.partner.membership_stop)
        self.assertEqual(self.next_month, self.partner.membership_cancel)
        self.assertEqual(
            self.reason.id, self.child.membership_last_withdrawal_reason_id.id
        )
        self.assertEqual(
            fields.Date.from_string("2016-06-07"),
            self.child.membership_last_withdrawal_date,
        )
        self.assertEqual(self.next_month, self.child.membership_stop)
        self.assertEqual(self.next_month, self.child.membership_cancel)
