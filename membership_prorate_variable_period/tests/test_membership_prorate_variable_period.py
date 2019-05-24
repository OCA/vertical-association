# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2015 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import datetime
from odoo import exceptions, fields
from odoo.tests import common


class TestMembershipProrateVariablePeriod(common.TransactionCase):

    def setUp(self):
        super(TestMembershipProrateVariablePeriod, self).setUp()
        self.product = self.env['product.product'].create(
            {
                'name': 'Membership product with prorate',
                'membership': True,
                'membership_prorate': True,
                'membership_type': 'variable',
                'membership_interval_qty': 1,
                'membership_interval_unit': 'weeks',
            })
        self.partner = self.env['res.partner'].create({'name': 'Test'})

    def test_create_invoice_membership_product_wo_prorate(self):
        self.product.membership_prorate = False
        account = self.partner.property_account_receivable_id.id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.today(),
            'account_id': account,
        })
        self.env['account.invoice.line'].create({
            'account_id': account,
            'product_id': self.product.id,
            'price_unit': self.product.list_price,
            'name': 'Membership w/o prorate',
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 1.0, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.membership_state, 'waiting')

    def test_create_invoice_membership_product_prorate_fixed(self):
        self.product.membership_type = 'fixed'
        self.product.membership_date_from = '2017-01-01'
        self.product.membership_date_to = '2017-12-31'
        account = self.partner.property_account_receivable_id.id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2017-04-01',
            'account_id': account,
        })
        self.env['account.invoice.line'].create({
            'account_id': account,
            'product_id': self.product.id,
            'price_unit': self.product.list_price,
            'name': 'Membership prorate fixed',
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.75, 2)

    def test_create_invoice_membership_product_prorate_week(self):
        account = self.partner.property_account_receivable_id.id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2015-01-01',  # It's thursday
            'account_id': account,
        })
        self.env['account.invoice.line'].create({
            'account_id': account,
            'product_id': self.product.id,
            'price_unit': self.product.list_price,
            'name': 'Membership with prorate',
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.43, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.member_lines[0].date_from,
                         fields.Date.from_string('2015-01-01'))
        self.assertEqual(self.partner.member_lines[0].date_to,
                         fields.Date.from_string('2015-01-04'))

    def test_create_invoice_membership_product_prorate_month(self):
        self.product.membership_interval_unit = 'months'
        account = self.partner.property_account_receivable_id.id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2015-04-15',
            'account_id': account,
        })
        self.env['account.invoice.line'].create({
            'account_id': account,
            'product_id': self.product.id,
            'price_unit': self.product.list_price,
            'name': 'Membership with prorate',
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.5, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.member_lines[0].date_from,
                         fields.Date.from_string('2015-04-15'))
        self.assertEqual(self.partner.member_lines[0].date_to,
                         fields.Date.from_string('2015-04-30'))

    def test_create_invoice_membership_product_prorate_year(self):
        self.product.membership_interval_unit = 'years'
        account = self.partner.property_account_receivable_id.id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2016-07-01',  # It's leap year
            'account_id': account,
        })
        self.env['account.invoice.line'].create({
            'account_id': account,
            'product_id': self.product.id,
            'price_unit': self.product.list_price,
            'name': 'Membership with prorate',
            'invoice_id': invoice.id,
            'quantity': 1.0,
        })
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.5, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.member_lines[0].date_from,
                         fields.Date.from_string('2016-07-01'))
        self.assertEqual(self.partner.member_lines[0].date_to,
                         fields.Date.from_string('2016-12-31'))

    def test_get_next_date(self):
        # Weeks
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = 'weeks'
        date = fields.Date.from_string('2015-07-01')
        self.assertEqual(
            datetime.date(day=6, month=7, year=2015),
            self.product._get_next_date(date))
        self.assertEqual(
            datetime.date(day=20, month=7, year=2015),
            self.product._get_next_date(date, qty=3))
        self.product.membership_interval_qty = 2
        self.assertEqual(
            datetime.date(day=10, month=8, year=2015),
            self.product._get_next_date(date, qty=3))
        # Months
        date = fields.Date.from_string('2015-07-31')
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = 'months'
        self.assertEqual(
            datetime.date(day=1, month=8, year=2015),
            self.product._get_next_date(date))
        self.assertEqual(
            datetime.date(day=1, month=10, year=2015),
            self.product._get_next_date(date, qty=3))
        self.product.membership_interval_qty = 2
        self.assertEqual(
            datetime.date(day=1, month=3, year=2016),
            self.product._get_next_date(date, qty=4))
        # Years
        date = fields.Date.from_string('2015-07-31')
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = 'years'
        self.assertEqual(
            datetime.date(day=1, month=1, year=2016),
            self.product._get_next_date(date))
        self.assertEqual(
            datetime.date(day=1, month=1, year=2018),
            self.product._get_next_date(date, qty=3))
        self.product.membership_interval_qty = 2
        self.assertEqual(
            datetime.date(day=1, month=1, year=2021),
            self.product._get_next_date(date, qty=3))

    def test_exceptions(self):
        # Test daily period
        self.product.membership_interval_qty = 1
        self.product.membership_interval_unit = 'days'
        with self.assertRaises(exceptions.Warning):
            self.product._get_next_date(fields.Date.from_string('2015-07-01'))
        with self.assertRaises(exceptions.Warning):
            account = self.partner.property_account_receivable_id.id
            invoice = self.env['account.invoice'].create({
                'partner_id': self.partner.id,
                'account_id': account,
            })
            self.env['account.invoice.line'].create({
                'account_id': account,
                'product_id': self.product.id,
                'price_unit': self.product.list_price,
                'name': 'Membership error',
                'invoice_id': invoice.id,
                'quantity': 1.0,
            })
