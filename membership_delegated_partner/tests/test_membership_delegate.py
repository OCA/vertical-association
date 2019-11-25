# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common


class TestMembershipDelegate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Mrs. Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test membership product",
                "membership": True,
                "membership_date_from": "2017-01-01",
                "membership_date_to": "2017-12-31",
            }
        )
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test", "type": "receivable", "internal_group": "asset"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test Sales Journal", "code": "tSAL", "type": "sale"}
        )

    def test_01_delegate(self):
        """ Delegates membership to partner 2 """
        invoice = self.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "type": "out_invoice",
                "partner_id": self.partner1.id,  # Invoicing partner
                "delegated_member_id": self.partner2.id,  # Delegate membership to
            }
        )
        self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "name": "Membership for delegate member",
                "account_id": self.account.id,
                "product_id": self.product.id,
                "price_unit": 1.0,
            }
        )
        self.assertTrue(self.partner2.member_lines, "Delegated partner gets the line")
        self.assertFalse(self.partner1.member_lines, "Invoicing partner gets no line")
        # We try to force reassign member line to another partner
        self.partner2.member_lines.partner = self.partner1
        self.assertFalse(self.partner1.member_lines, "It's going to stand on partner2")
        # Same test, with account_invoice_line in the write
        self.partner2.member_lines.write(
            {
                "partner": self.partner1.id,
                "account_invoice_line": invoice.invoice_line_ids[0].id,
            }
        )
        self.assertFalse(self.partner1.member_lines, "It's going to stand on partner2")

    def test_02_change_delegated_member(self):
        """ Delegated member can be changed later """
        invoice = self.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "type": "out_invoice",
                "partner_id": self.partner1.id,  # Invoicing partner
            }
        )
        self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "name": "Membership classic",
                "account_id": self.account.id,
                "product_id": self.product.id,
                "price_unit": 1.0,
            }
        )
        self.assertTrue(self.partner1.member_lines, "Partner gets the line")
        invoice.delegated_member_id = self.partner2
        self.assertTrue(self.partner2.member_lines, "Delegate gets the line")
        self.assertFalse(self.partner1.member_lines, "Partner drops the line")

        invoice.delegated_member_id = False
        self.assertFalse(self.partner2.member_lines, "Delegate drops the line")
        self.assertTrue(self.partner1.member_lines, "Partner gets the line")

    def test_03_refund_invoice_delegated_partner(self):
        """ A refund should inherit the delegated partner in the invoice """
        invoice = self.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "type": "out_invoice",
                "partner_id": self.partner1.id,  # Invoicing partner
                "delegated_member_id": self.partner2.id,  # Delegate membership to
            }
        )
        self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "name": "Membership for delegate member",
                "account_id": self.account.id,
                "product_id": self.product.id,
                "price_unit": 1.0,
            }
        )
        invoice.action_post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "refund_method": "refund",
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertEqual(refund.delegated_member_id, self.partner2)

    def test_04_get_partner_for_membership(self):
        """ Auxiliary method to get the member """
        invoice = self.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "type": "out_invoice",
                "partner_id": self.partner1.id,  # Invoicing partner
                "delegated_member_id": self.partner2.id,  # Delegate membership to
            }
        )
        self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "name": "Membership for delegate member",
                "account_id": self.account.id,
                "product_id": self.product.id,
                "price_unit": 1.0,
            }
        )
        get_member = invoice.invoice_line_ids[0]._get_partner_for_membership
        self.assertEqual(get_member(), self.partner2)
        invoice.delegated_member_id = False
        self.assertEqual(get_member(), self.partner1)
