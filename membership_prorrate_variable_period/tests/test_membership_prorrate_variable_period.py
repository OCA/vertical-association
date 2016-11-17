# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import datetime
from dateutil.relativedelta import relativedelta
from openerp import exceptions, fields
import openerp.tests.common as common


class TestMembershipProrrateVariablePeriod(common.TransactionCase):

    def setUp(self):
        super(TestMembershipProrrateVariablePeriod, self).setUp()
        self.product = self.env['product.product'].create(
            {
                'name': 'Membership product with prorrate',
                'membership': True,
                'membership_prorrate': True,
                'membership_type': 'variable',
                'membership_interval_qty': 1,
                'membership_interval_unit': 'weeks',
            })
        self.partner = self.env['res.partner'].create({'name': 'Test'})

    def test_create_invoice_membership_product_wo_prorrate(self):
        self.product.membership_prorrate = False
        invoice = self.env['account.invoice'].create(
            {'partner_id': self.partner.id,
             'date_invoice': fields.Date.today(),
             'account_id': self.partner.property_account_receivable.id,
             'invoice_line': [(0, 0, {'product_id': self.product.id,
                                      'name': 'Membership w/o prorrate'})]})
        self.assertAlmostEqual(invoice.invoice_line[0].quantity, 1.0, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.membership_state, 'waiting')

    def test_create_invoice_membership_product_prorrate_fixed(self):
        self.product.membership_type = 'fixed'
        self.product.membership_date_from = fields.Date.to_string(
            datetime.date.today() + relativedelta(month=1, day=1))
        self.product.membership_date_to = fields.Date.to_string(
            datetime.date.today() + relativedelta(month=12, months=1, day=1,
                                                  days=-1))
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.context_today(self.product),
            'account_id': self.partner.property_account_receivable.id,
            'invoice_line': [(0, 0, {
                'product_id': self.product.id,
                'name': 'Membership prorrate fixed',
            })],
        })
        self.assertAlmostEqual(
            invoice.invoice_line[0].quantity,
            1 - (
                datetime.date.today() -
                fields.Date.from_string(self.product.membership_date_from)
            ).days / float(365),
            2)
        self.assertEqual(self.partner.membership_state, 'waiting')

    def test_create_invoice_membership_product_prorrate_week(self):
        invoice = self.env['account.invoice'].create(
            {'partner_id': self.partner.id,
             'date_invoice': '2015-01-01',  # It's thursday
             'account_id': self.partner.property_account_receivable.id,
             'invoice_line': [(0, 0, {'product_id': self.product.id,
                                      'name': 'Membership with prorrate'})]})
        # Result is rounded to 2 decimals for avoiding the fail in tests
        # if "Product Unit of Measure" precision changes in the future
        self.assertAlmostEqual(invoice.invoice_line[0].quantity, 0.43, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.member_lines[0].date_from, '2015-01-01')
        self.assertEqual(self.partner.member_lines[0].date_to, '2015-01-04')

    def test_create_invoice_membership_product_prorrate_month(self):
        self.product.membership_interval_unit = 'months'
        invoice = self.env['account.invoice'].create(
            {'partner_id': self.partner.id,
             'date_invoice': '2015-04-15',
             'account_id': self.partner.property_account_receivable.id,
             'invoice_line': [(0, 0, {'product_id': self.product.id,
                                      'name': 'Membership with prorrate'})]})
        # Result is rounded to 2 decimals for avoiding the fail in tests
        # if "Product Unit of Measure" precision changes in the future
        self.assertAlmostEqual(invoice.invoice_line[0].quantity, 0.5, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.member_lines[0].date_from, '2015-04-15')
        self.assertEqual(self.partner.member_lines[0].date_to, '2015-04-30')

    def test_create_invoice_membership_product_prorrate_year(self):
        self.product.membership_interval_unit = 'years'
        invoice = self.env['account.invoice'].create(
            {'partner_id': self.partner.id,
             'date_invoice': '2016-07-01',  # It's leap year
             'account_id': self.partner.property_account_receivable.id,
             'invoice_line': [(0, 0, {'product_id': self.product.id,
                                      'name': 'Membership with prorrate'})]})
        # Result is rounded to 2 decimals for avoiding the fail in tests
        # if "Product Unit of Measure" precision changes in the future
        self.assertAlmostEqual(invoice.invoice_line[0].quantity, 0.5, 2)
        self.assertTrue(self.partner.member_lines)
        self.assertEqual(self.partner.member_lines[0].state, 'waiting')
        self.assertEqual(self.partner.member_lines[0].date_from, '2016-07-01')
        self.assertEqual(self.partner.member_lines[0].date_to, '2016-12-31')

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
            self.env['account.invoice'].create(
                {'partner_id': self.partner.id,
                 'account_id': self.partner.property_account_receivable.id,
                 'invoice_line': [(0, 0, {'product_id': self.product.id,
                                          'name': 'Membership error'})]})
