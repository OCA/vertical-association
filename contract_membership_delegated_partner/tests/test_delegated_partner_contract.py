# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestMembershipDelegateSetup(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super(TestMembershipDelegateSetup, cls).setUpClass()
        cls.partner2 = cls.env["res.partner"].create({"name": "Mrs. Odoo"})
        cls.product_1.membership = True
        cls.contract.delegated_member_id = cls.partner2

    def test_01_generate_and_delegate(self):
        """ Invoices to a partner delegates membership to another one """
        self.contract.recurring_create_invoice()
        # The contract and invoicing partner has no membership
        self.assertFalse(self.partner.member_lines)
        # It goes to the delegated partner
        self.assertTrue(self.partner2.member_lines)
