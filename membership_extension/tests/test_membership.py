# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from openerp import fields
from openerp.exceptions import Warning as UserError
from openerp.tests.common import TransactionCase


class TestMembership(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMembership, self).setUp(*args, **kwargs)
        self.next_two_months = fields.Date.to_string(
            fields.Date.from_string(fields.Date.today()) + timedelta(days=60))
        self.next_month = fields.Date.to_string(
            fields.Date.from_string(fields.Date.today()) + timedelta(days=30))
        self.yesterday = fields.Date.to_string(
            fields.Date.from_string(fields.Date.today()) - timedelta(days=1))
        self.category_gold = self.env.ref(
            'membership_extension.membership_category_gold')
        self.category_silver = self.env.ref(
            'membership_extension.membership_category_silver')
        self.partner = self.env['res.partner'].create({
            'name': 'Test company',
        })
        self.child = self.env['res.partner'].create({
            'name': 'Test child',
            'associate_member': self.partner.id,
        })
        self.gold_product = self.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Gold',
            'membership': True,
            'membership_date_from': '2016-02-01',
            'membership_date_to': self.next_two_months,
            'membership_category_id': self.category_gold.id,
            'list_price': 100.00,
        })
        self.silver_product = self.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Silver',
            'membership': True,
            'membership_date_from': '2016-02-01',
            'membership_date_to': self.next_month,
            'membership_category_id': self.category_silver.id,
            'list_price': 50.00,
        })

    def test_compute_membership(self):
        line = self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': '2016-03-01',
            'date_from': '2016-02-01',
            'date_to': self.next_two_months,
            'partner': self.partner.id,
            'state': 'waiting',
        })
        self.assertEqual('waiting', self.partner.membership_state)
        self.assertFalse(self.partner.membership_start)
        self.assertFalse(self.partner.membership_last_start)
        self.assertFalse(self.partner.membership_stop)
        self.assertFalse(self.partner.membership_cancel)
        self.assertEqual('waiting', self.child.membership_state)
        self.assertFalse(self.child.membership_start)
        self.assertFalse(self.child.membership_last_start)
        self.assertFalse(self.child.membership_stop)
        self.assertFalse(self.child.membership_cancel)
        line.write({
            'state': 'invoiced',
        })
        self.assertEqual('invoiced', self.partner.membership_state)
        self.assertEqual('2016-02-01', self.partner.membership_start)
        self.assertEqual('2016-02-01', self.partner.membership_last_start)
        self.assertEqual(self.next_two_months, self.partner.membership_stop)
        self.assertFalse(self.partner.membership_cancel)
        self.assertEqual('invoiced', self.child.membership_state)
        self.assertEqual('2016-02-01', self.child.membership_start)
        self.assertEqual('2016-02-01', self.child.membership_last_start)
        self.assertEqual(self.next_two_months, self.child.membership_stop)
        self.assertFalse(self.child.membership_cancel)
        line.write({
            'date_cancel': self.yesterday,
        })
        self.assertEqual('old', self.partner.membership_state)
        self.assertEqual('2016-02-01', self.partner.membership_start)
        self.assertEqual('2016-02-01', self.partner.membership_last_start)
        self.assertEqual(self.yesterday, self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual('old', self.child.membership_state)
        self.assertEqual('2016-02-01', self.child.membership_start)
        self.assertEqual('2016-02-01', self.child.membership_last_start)
        self.assertEqual(self.yesterday, self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        line.write({
            'state': 'canceled',
        })
        self.assertEqual('none', self.partner.membership_state)
        self.assertFalse(self.partner.membership_start)
        self.assertFalse(self.partner.membership_last_start)
        self.assertFalse(self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual('none', self.child.membership_state)
        self.assertFalse(self.child.membership_start)
        self.assertFalse(self.child.membership_last_start)
        self.assertFalse(self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        other_line = self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': '2016-05-01',
            'date_from': '2016-04-01',
            'date_to': self.next_two_months,
            'partner': self.partner.id,
            'state': 'waiting',
        })
        self.assertEqual('waiting', self.partner.membership_state)
        self.assertFalse(self.partner.membership_start)
        self.assertFalse(self.partner.membership_last_start)
        self.assertFalse(self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual('waiting', self.child.membership_state)
        self.assertFalse(self.child.membership_start)
        self.assertFalse(self.child.membership_last_start)
        self.assertFalse(self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        other_line.write({
            'state': 'paid',
        })
        self.assertEqual('paid', self.partner.membership_state)
        self.assertEqual('2016-04-01', self.partner.membership_start)
        self.assertEqual('2016-04-01', self.partner.membership_last_start)
        self.assertEqual(self.next_two_months, self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual('paid', self.child.membership_state)
        self.assertEqual('2016-04-01', self.child.membership_start)
        self.assertEqual('2016-04-01', self.child.membership_last_start)
        self.assertEqual(self.next_two_months, self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)

    def test_category(self):
        line_one = self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': '2016-03-01',
            'date_from': '2016-02-01',
            'date_to': self.next_two_months,
            'partner': self.partner.id,
            'state': 'invoiced',
        })
        self.assertEqual([self.category_gold.id],
                         self.partner.membership_category_ids.ids)
        self.assertEqual('Gold', self.partner.membership_categories)
        self.assertEqual([self.category_gold.id],
                         self.child.membership_category_ids.ids)
        self.assertEqual('Gold', self.child.membership_categories)
        line_two = self.env['membership.membership_line'].create({
            'membership_id': self.silver_product.id,
            'member_price': 50.00,
            'date': '2016-04-01',
            'date_from': '2016-05-01',
            'date_to': self.next_month,
            'partner': self.partner.id,
            'state': 'paid',
        })
        self.assertEqual(set([self.category_gold.id, self.category_silver.id]),
                         set(self.partner.membership_category_ids.ids))
        self.assertTrue('Silver' in self.partner.membership_categories)
        self.assertTrue('Gold' in self.partner.membership_categories)
        self.assertEqual(set([self.category_gold.id, self.category_silver.id]),
                         set(self.child.membership_category_ids.ids))
        self.assertTrue('Silver' in self.child.membership_categories)
        self.assertTrue('Gold' in self.child.membership_categories)
        line_one.write({
            'state': 'canceled',
        })
        self.assertEqual([self.category_silver.id],
                         self.partner.membership_category_ids.ids)
        self.assertEqual('Silver', self.partner.membership_categories)
        self.assertEqual([self.category_silver.id],
                         self.child.membership_category_ids.ids)
        self.assertEqual('Silver', self.child.membership_categories)
        line_two.write({
            'state': 'waiting',
        })
        self.assertFalse(self.partner.membership_category_ids.ids)
        self.assertFalse(self.partner.membership_categories)
        self.assertFalse(self.child.membership_category_ids.ids)
        self.assertFalse(self.child.membership_categories)

    def test_remove_membership_line_with_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2016-07-01',
            'account_id': self.partner.property_account_receivable.id,
            'invoice_line': [(0, 0, {
                'product_id': self.gold_product.id,
                'name': 'Membership',
            })],
        })
        with self.assertRaises(UserError):
            self.partner.member_lines[0].unlink()
        invoice.invoice_line.unlink()
        self.assertFalse(self.partner.member_lines)

    def test_membership_line_onchange(self):
        line = self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': '2016-03-01',
            'partner': self.partner.id,
            'state': 'invoiced',
        })
        line._onchange_date()
        self.assertEqual(100.00, line.member_price)
        self.assertEqual('2016-03-01', line.date_from)
        self.assertEqual(self.next_two_months, line.date_to)
        line.write({
            'membership_id': self.silver_product.id,
        })
        line._onchange_membership_id()
        self.assertEqual(50, line.member_price)
        self.assertEqual('2016-03-01', line.date_from)
        self.assertEqual(self.next_month, line.date_to)

    def test_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2016-07-01',
            'account_id': self.partner.property_account_receivable.id,
            'invoice_line': [(0, 0, {
                'product_id': self.gold_product.id,
                'name': 'Membership',
                'quantity': 1.0,
                'price_unit': 100.00,
            })],
        })
        invoice.button_reset_taxes()
        invoice.journal_id.update_posted = True
        line = self.partner.member_lines[0]
        self.assertEqual('waiting', line.state)
        self.assertEqual('2016-07-01', line.date_from)
        self.assertEqual(self.next_two_months, line.date_to)
        invoice.signal_workflow('invoice_open')
        self.assertEqual('invoiced', line.state)
        invoice.confirm_paid()
        self.assertEqual('paid', line.state)
        invoice.action_cancel()
        self.assertEqual('canceled', line.state)
        invoice.action_cancel_draft()
        self.assertEqual('waiting', line.state)
        invoice.signal_workflow('invoice_open')
        invoice.confirm_paid()
        self.assertEqual('paid', line.state)
        refund = invoice.refund()
        invoice.button_reset_taxes()
        refund.journal_id.update_posted = True
        refund.signal_workflow('invoice_open')
        self.assertEqual('canceled', line.state)
        refund.action_cancel()
        self.assertEqual('paid', line.state)
        refund.action_cancel_draft()
        refund.invoice_line[0].quantity = 0.5
        invoice.button_reset_taxes()
        self.assertNotEqual(invoice.amount_untaxed, refund.amount_untaxed)
        refund.signal_workflow('invoice_open')

        self.assertEqual('paid', line.state)

    def test_check_membership_all(self):
        self.env['res.partner'].check_membership_all()
