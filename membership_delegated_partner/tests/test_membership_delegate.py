# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form, TransactionCase


class TestMembershipDelegate(TransactionCase):
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
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "account_type": "income",
                "reconcile": True,
            }
        )
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test Sales Journal", "code": "tSAL", "type": "sale"}
        )

    def test_01_delegate(self):
        """Delegates membership to partner 2"""
        invoice = self.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "move_type": "out_invoice",
                "partner_id": self.partner1.id,  # Invoicing partner
                "delegated_member_id": self.partner2.id,  # Delegate membership to
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "display_type": "product",
                            "name": "Membership for delegate member",
                            "account_id": self.account.id,
                            "product_id": self.product.id,
                            "price_unit": 1.0,
                        },
                    )
                ],
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
        """Delegated member can be changed later"""
        invoice = self.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "move_type": "out_invoice",
                "partner_id": self.partner1.id,  # Invoicing partner
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "display_type": "product",
                            "name": "Membership classic",
                            "account_id": self.account.id,
                            "product_id": self.product.id,
                            "price_unit": 1.0,
                        },
                    )
                ],
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
        """A refund should inherit the delegated partner in the invoice"""
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.partner1
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.price_unit = 1.0
        invoice = move_form.save()
        invoice.write({"delegated_member_id": self.partner2.id})
        invoice.action_post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "refund_method": "refund",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertEqual(refund.delegated_member_id, self.partner2)

    def test_04_get_partner_for_membership(self):
        """Auxiliary method to get the member"""
        invoice = self.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "move_type": "out_invoice",
                "partner_id": self.partner1.id,  # Invoicing partner
                "delegated_member_id": self.partner2.id,  # Delegate membership to
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "display_type": "product",
                            "name": "Membership for delegate member",
                            "account_id": self.account.id,
                            "product_id": self.product.id,
                            "price_unit": 1.0,
                        },
                    )
                ],
            }
        )
        get_member = invoice.invoice_line_ids[0]._get_partner_for_membership
        self.assertEqual(get_member(), self.partner2)
        invoice.delegated_member_id = False
        self.assertEqual(get_member(), self.partner1)
