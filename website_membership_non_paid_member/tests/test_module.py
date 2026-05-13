# Copyright 2026-Today OCA France - Sylvain LE GAL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.membership.tests.common import TestMembershipCommon


@tagged("post_install", "-at_install")
class TestMembership(TestMembershipCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ICP = cls.env["ir.config_parameter"].sudo()
        cls.MembershipLine = cls.env["membership.membership_line"]
        cls.MembershipLineWithContext = cls.env[
            "membership.membership_line"
        ].with_context(include_not_paid_member=True)

    def _get_displayed_members(self, with_context=False):
        if with_context:
            lines = self.MembershipLineWithContext.search([("state", "=", "paid")])
        else:
            lines = self.MembershipLine.search([("state", "=", "paid")])
        return lines.mapped("partner")

    def _set_feature(self, feature_name, feature_value):
        self.ICP.set_param(
            f"website_membership_non_paid_member.{feature_name}",
            feature_value,
        )

    def test_search(self):
        self._set_feature("website_display_waiting_membership", False)
        self._set_feature("website_display_invoiced_membership", False)

        self.assertEqual(self.partner_1.membership_state, "none")

        # subscribes to a membership (Draft State)
        invoice = self.partner_1.create_membership_invoice(self.membership_1, 75.0)

        self.assertEqual(self.partner_1.membership_state, "waiting")

        self.assertNotIn(self.partner_1, self._get_displayed_members())
        self.assertNotIn(self.partner_1, self._get_displayed_members(with_context=True))

        self._set_feature("website_display_waiting_membership", True)

        self.assertNotIn(self.partner_1, self._get_displayed_members())
        self.assertIn(self.partner_1, self._get_displayed_members(with_context=True))

        self._set_feature("website_display_waiting_membership", False)

        # Confirmed the membership (Invoiced State)
        invoice.action_post()
        self.assertEqual(self.partner_1.membership_state, "invoiced")

        self.assertNotIn(self.partner_1, self._get_displayed_members())
        self.assertNotIn(self.partner_1, self._get_displayed_members(with_context=True))

        self._set_feature("website_display_invoiced_membership", True)

        self.assertNotIn(self.partner_1, self._get_displayed_members())
        self.assertIn(self.partner_1, self._get_displayed_members(with_context=True))

        self._set_feature("website_display_invoiced_membership", False)

        # Pay the membership (Paid State)
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create(
            {
                "amount": 86.25,
                "payment_method_line_id": self.inbound_payment_method_line.id,
            }
        )._create_payments()

        self.assertEqual(self.partner_1.membership_state, "paid")

        self.assertIn(self.partner_1, self._get_displayed_members())
        self.assertIn(self.partner_1, self._get_displayed_members(with_context=True))
