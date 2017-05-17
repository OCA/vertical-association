# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestMembershipInitialFee(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMembershipInitialFee, cls).setUpClass()
        cls.product_category = cls.env['product.category'].create({
            'name': 'test_cat',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'list_price': 100,
        })
        cls.product_fee = cls.env['product.product'].create({
            'name': 'Membership Fee',
            'list_price': 1.0,
            'type': 'service',
            'categ_id': cls.product_category.id,
        })
        cls.product_fixed = cls.env['product.product'].create({
            'name': 'Membership product with fixed initial fee',
            'membership': True,
            'initial_fee': 'fixed',
            'product_fee': cls.product_fee.id,
            'fixed_fee': 50.0,
            'list_price': 150.0,
            'type': 'service',
            'categ_id': cls.product_category.id,
        })
        cls.product_percentage = cls.env['product.product'].create({
            'name': 'Membership product with percentage initial fee',
            'membership': True,
            'product_fee': cls.product_fee.id,
            'initial_fee': 'percentage',
            'percentage_fee': 10.0,
            'list_price': 150.0,
            'type': 'service',
            'categ_id': cls.product_category.id,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test',
        })

    def check_membership_invoice(self, invoice, expected_amount):
        self.assertEqual(
            len(invoice.invoice_line_ids), 2,
            "The created invoice should have 2 lines")
        initial_fee_line = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_fee)
        self.assertEqual(
            initial_fee_line.price_unit, expected_amount,
            "The initial fee amount is not correct")

    def test_create_invoice_wo_initial_fee(self):
        self.product_fixed.initial_fee = 'none'
        invoice_id = self.partner.create_membership_invoice(
            product_id=self.product_fixed.id, datas={'amount': 1.0})
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(
            len(invoice.invoice_line_ids), 1,
            "The created invoice should have 1 lines")

    def test_create_invoice_initial_fee_fixed(self):
        invoice_id = self.partner.create_membership_invoice(
            product_id=self.product_fixed.id, datas={'amount': 1.0})
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.check_membership_invoice(invoice, 50.0)

    def test_create_invoice_initial_fee_percentage(self):
        invoice_id = self.partner.create_membership_invoice(
            product_id=self.product_percentage.id,
            datas={'amount': 150.0})[0]
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.check_membership_invoice(invoice, 15.0)

    def test_create_invoice_initial_fee_taxes(self):
        tax = self.env['account.tax'].create({
            'name': 'Tax',
            'amount_type': 'percent',
            'amount': 0.10,
        })
        self.product_fixed.product_fee.taxes_id = tax
        invoice_id = self.partner.create_membership_invoice(
            product_id=self.product_fixed.id,
            datas={'amount': 150.0},
        )[0]
        invoice = self.env['account.invoice'].browse(invoice_id)
        initial_fee_line = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_fee)
        self.assertEqual(initial_fee_line.invoice_line_tax_ids, tax)

    def test_onchange_product_fee(self):
        membership_product = self.env['product.template'].new({
            'name': 'Test membership product',
        })
        membership_product.product_fee = self.product
        membership_product.onchange_product_fee()
        self.assertEqual(membership_product.fixed_fee, self.product.list_price)
