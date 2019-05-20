# Copyright 2019 Yu Weng <yweng@elegosoft.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common


class TestMembership(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMembership, cls).setUpClass()
        date_today = fields.Date.from_string(fields.Date.today())
        cls.next_month = fields.Date.to_string(date_today + timedelta(days=30))
        cls.tax_15p = cls.env['account.tax'].create({
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'name': "Tax 15%",
            'amount': 15,
            'active': True,
        })
        cls.account_partner_type = cls.env['account.account.type'].create({
            'name': 'Test partner account type',
            'type': 'receivable',
        })
        cls.account_partner = cls.env['account.account'].create({
            'name': 'Test partner account',
            'code': 'PARTNER',
            'user_type_id': cls.account_partner_type.id,
            'reconcile': True,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'free_member': True,
            'property_account_receivable_id': cls.account_partner.id,
        })
        cls.partner_wo_account = cls.env['res.partner'].create({
            'name': 'Test Contact WO Account',
            'property_account_receivable_id': False,
        })
        cls.gold_product = cls.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Gold',
            'membership': True,
            'membership_date_from': fields.Date.today(),
            'membership_date_to': cls.next_month,
            'list_price': 100.00,
            'taxes_id': [(4, cls.tax_15p.id, False)]
        })
        cls.silver_product = cls.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Silver',
            'membership': True,
            'membership_date_from': fields.Date.today(),
            'membership_date_to': cls.next_month,
            'list_price': 50.00,
        })
        cls.basic_product = cls.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Basic',
            'membership': True,
            'membership_date_from': fields.Date.today(),
            'membership_date_to': cls.next_month,
            'list_price': 20.00,
        })
        cls.product_set = cls.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Set',
            'membership': True,
            'membership_set': True,
            'membership_date_from': fields.Date.today(),
            'membership_date_to': cls.next_month,
            'list_price': 150.00,
            'membership_set_products': [
                (4, cls.gold_product.id, False),
                (4, cls.silver_product.id, False),
            ]
        })

    def test_membership_invoice(self):
        wizard = self.env['membership.invoice'].with_context(
            active_ids=[self.partner.id],
            active_model='res.partner'
        ).create({
            'product_id': self.product_set.id,
            'member_price': 150,
        })
        with self.assertRaisesRegexp(
            UserError,
            r'Partner is a free Member'
        ):
            invoice_id = wizard.membership_invoice()['domain'][0][2]

        self.partner.free_member = False
        invoice_id = wizard.membership_invoice()['domain'][0][2]
        invoice = self.env['account.invoice'].browse(invoice_id)
        for line in invoice.invoice_line_ids:
            if line.product_id.id == self.gold_product.id:
                self.assertEqual(line.price_unit, 100)
                self.assertEqual(
                    line.invoice_line_tax_ids[0].id,
                    self.tax_15p.id)
            elif line.product_id.id == self.silver_product.id:
                self.assertEqual(line.price_unit, 50)
                self.assertEqual(len(line.invoice_line_tax_ids), 0)
            else:
                self.assertTrue(False)
        self.assertEqual(invoice.amount_untaxed, 150)
        self.assertEqual(invoice.amount_tax, 15)
        self.assertEqual(invoice.amount_total, 165)

        wizard = self.env['membership.invoice'].with_context(
            active_ids=[self.partner_wo_account.id],
            active_model='res.partner'
        ).create({
            'product_id': self.product_set.id,
            'member_price': 150,
        })
        with self.assertRaisesRegexp(
            UserError,
            r"Partner doesn't have an account to make the invoice"
        ):
            invoice_id = wizard.membership_invoice()['domain'][0][2]

        wizard = self.env['membership.invoice'].with_context(
            active_ids=[self.partner.id],
            active_model='res.partner'
        ).create({
            'product_id': self.basic_product.id,
            'member_price': 100,
        })
        wizard.membership_invoice()
