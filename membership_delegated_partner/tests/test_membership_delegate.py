# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.membership.tests.common import TestMembershipCommon


class TestMembershipDelegate(TestMembershipCommon):
    def test_01_delegate(self):
        """Delegates membership to partner 2"""
        invoice = self.partner_1.create_membership_invoice(self.membership_1, 1.0)
        invoice.delegated_member_id = self.partner_2
        self.assertTrue(
            self.partner_2.member_line_ids, "Delegated partner gets the line"
        )
        self.assertFalse(
            self.partner_1.member_line_ids, "Invoicing partner gets no line"
        )
        # We try to force reassign member line to another partner
        self.partner_2.member_line_ids.partner_id = self.partner_1
        self.assertFalse(
            self.partner_1.member_line_ids, "It's going to stand on partner2"
        )
        # Same test, with account_invoice_line_id in the write
        self.partner_2.member_line_ids.write(
            {
                "partner_id": self.partner_1.id,
                "account_invoice_line_id": invoice.invoice_line_ids[0].id,
            }
        )
        self.assertFalse(
            self.partner_1.member_line_ids, "It's going to stand on partner2"
        )

    def test_02_change_delegated_member(self):
        """Delegated member can be changed later"""
        invoice = self.partner_1.create_membership_invoice(self.membership_1, 1.0)
        self.assertTrue(self.partner_1.member_line_ids, "Partner gets the line")
        invoice.delegated_member_id = self.partner_2
        self.assertTrue(self.partner_2.member_line_ids, "Delegate gets the line")
        self.assertFalse(self.partner_1.member_line_ids, "Partner drops the line")
        invoice.delegated_member_id = False
        self.assertFalse(self.partner_2.member_line_ids, "Delegate drops the line")
        self.assertTrue(self.partner_1.member_line_ids, "Partner gets the line")

    @mute_logger("odoo.models.unlink")
    def test_03_refund_invoice_delegated_partner(self):
        """A refund should inherit the delegated partner in the invoice"""
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.partner_1
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.membership_1
            line_form.price_unit = 1.0
        invoice = move_form.save()
        invoice.write({"delegated_member_id": self.partner_2.id})
        invoice.action_post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertEqual(refund.delegated_member_id, self.partner_2)

    def test_04_get_partner_for_membership(self):
        invoice = self.partner_1.create_membership_invoice(self.membership_1, 1.0)
        invoice.delegated_member_id = self.partner_2
        membership_line = invoice.invoice_line_ids.membership_line_ids
        self.assertEqual(membership_line.partner_id, self.partner_2)
        invoice.delegated_member_id = False
        self.assertEqual(membership_line.partner_id, self.partner_1)
