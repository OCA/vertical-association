# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common
from odoo import fields


class TestMembershipProrate(common.TransactionCase):

    def setUp(self):
        super(TestMembershipProrate, self).setUp()
        self.product = self.env['product.product'].create(
            {
                'name': 'Membership product with prorate',
                'membership': True,
                'membership_prorate': True,
                'membership_date_from': '2017-01-01',
                'membership_date_to': '2017-12-31',
            })
        self.partner = self.env['res.partner'].create({'name': 'Test'})

    def test_create_invoice_membership_product_wo_prorate(self):
        self.product.membership_prorate = False
        invoice_id = self.partner.create_membership_invoice(
            product_id=self.product.id, datas={'amount': 1.0})
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, 1.0)

    def test_create_invoice_membership_product_prorate(self):
        account = self.partner.property_account_receivable_id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2017-07-01',
            'account_id': account.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': self.product.id,
            'price_unit': 100.0,
            'name': 'Membership with prorate',
            'account_id': account.id,
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        # Result is rounded to 2 decimals for avoiding the fail in tests
        # if "Product Unit of Measure" precision changes in the future
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.50, 2)
        memb_line = self.env['membership.membership_line'].search(
            [('account_invoice_line', '=', invoice.invoice_line_ids[0].id)],
            limit=1)
        self.assertAlmostEqual(memb_line.member_price, 50.00, 2)
        self.assertEqual(memb_line.date_from,
                         fields.Date.from_string('2017-07-01'))
        # Set the date six months before the membership period
        invoice.date_invoice = '2016-07-01'
        self.env['account.invoice.line'].create({
            'product_id': self.product.id,
            'price_unit': 100.0,
            'name': 'Membership with prorate',
            'account_id': account.id,
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        # The whole period is calculated
        self.assertAlmostEqual(invoice.invoice_line_ids[1].quantity, 1.0, 2)
        memb_line = self.env['membership.membership_line'].search(
            [('account_invoice_line', '=', invoice.invoice_line_ids[1].id)],
            limit=1)
        self.assertAlmostEqual(memb_line.member_price, 100.00, 2)
        self.assertEqual(memb_line.date_from,
                         fields.Date.from_string('2017-01-01'))
        # Set the date six months after the membership period
        invoice.date_invoice = '2018-07-01'
        self.env['account.invoice.line'].create({
            'product_id': self.product.id,
            'price_unit': 100.0,
            'name': 'Membership with prorate',
            'account_id': account.id,
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        # Nothing to invoice
        self.assertAlmostEqual(invoice.invoice_line_ids[2].quantity, 0, 2)
        memb_line = self.env['membership.membership_line'].search(
            [('account_invoice_line', '=', invoice.invoice_line_ids[2].id)],
            limit=1)
        self.assertAlmostEqual(memb_line.member_price, 0.00, 2)
        self.assertEqual(memb_line.date_from,
                         fields.Date.from_string('2017-12-31'))
