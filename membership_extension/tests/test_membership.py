# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import fields
from odoo.exceptions import UserError
from psycopg2 import IntegrityError
from odoo.tests import common


class TestMembership(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMembership, cls).setUpClass()
        date_today = fields.Date.from_string(fields.Date.today())
        cls.account_bank_type = cls.env['account.account.type'].create({
            'name': 'Test bank account type',
            'type': 'liquidity',
        })
        cls.account_bank = cls.env['account.account'].create({
            'name': 'Test bank account',
            'code': 'BANK',
            'user_type_id': cls.account_bank_type.id,
            'reconcile': True,
        })
        cls.journal = cls.env['account.journal'].create({
            'name': 'Test journal',
            'code': 'TEST',
            'type': 'general',
            'update_posted': True,
            'default_debit_account_id': cls.account_bank.id,
            'default_credit_account_id': cls.account_bank.id,
        })
        cls.bank_journal = cls.env['account.journal'].create({
            'name': 'Test bank journal',
            'code': 'TB',
            'type': 'bank',
            'update_posted': True,
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
        cls.account_product_type = cls.env['account.account.type'].create({
            'name': 'Test product account type',
            'type': 'other',
        })
        cls.account_product = cls.env['account.account'].create({
            'name': 'Test product account',
            'code': 'PRODUCT',
            'user_type_id': cls.account_product_type.id,
        })
        cls.next_two_months = fields.Date.to_string(
            date_today + timedelta(days=60)
        )
        cls.next_month = fields.Date.to_string(date_today + timedelta(days=30))
        cls.yesterday = fields.Date.to_string(date_today - timedelta(days=1))
        cls.category_gold = cls.env.ref(
            'membership_extension.membership_category_gold'
        )
        cls.category_silver = cls.env.ref(
            'membership_extension.membership_category_silver'
        )
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'property_account_receivable_id': cls.account_partner.id,
        })
        cls.child = cls.env['res.partner'].create({
            'name': 'Test child',
            'associate_member': cls.partner.id,
        })
        cls.gold_product = cls.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Gold',
            'membership': True,
            'membership_date_from': fields.Date.today(),
            'membership_date_to': cls.next_month,
            'membership_category_id': cls.category_gold.id,
            'list_price': 100.00,
        })
        cls.silver_product = cls.env['product.product'].create({
            'type': 'service',
            'name': 'Membership Silver',
            'membership': True,
            'membership_date_from': fields.Date.today(),
            'membership_date_to': cls.next_two_months,
            'membership_category_id': cls.category_silver.id,
            'list_price': 50.00,
        })
        cls.current_year = date_today.year

    def test_compute_membership(self):
        line = self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': fields.Date.today(),
            'date_from': fields.Date.today(),
            'date_to': self.next_month,
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
        self.assertEqual(fields.Date.today(), self.partner.membership_start)
        self.assertEqual(
            fields.Date.today(), self.partner.membership_last_start,
        )
        self.assertEqual(self.next_month, self.partner.membership_stop)
        self.assertFalse(self.partner.membership_cancel)
        self.assertEqual('invoiced', self.child.membership_state)
        self.assertEqual(fields.Date.today(), self.child.membership_start)
        self.assertEqual(fields.Date.today(), self.child.membership_last_start)
        self.assertEqual(self.next_month, self.child.membership_stop)
        self.assertFalse(self.child.membership_cancel)
        line.write({
            'date_cancel': self.yesterday,
        })
        self.assertEqual('old', self.partner.membership_state)
        self.assertEqual(fields.Date.today(), self.partner.membership_start)
        self.assertEqual(
            fields.Date.today(), self.partner.membership_last_start,
        )
        self.assertEqual(self.yesterday, self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual('old', self.child.membership_state)
        self.assertEqual(fields.Date.today(), self.child.membership_start)
        self.assertEqual(fields.Date.today(), self.child.membership_last_start)
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
            'membership_id': self.silver_product.id,
            'member_price': 100.00,
            'date': fields.Date.today(),
            'date_from': fields.Date.today(),
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
        self.assertEqual(fields.Date.today(), self.partner.membership_start)
        self.assertEqual(
            fields.Date.today(), self.partner.membership_last_start,
        )
        self.assertEqual(self.next_two_months, self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual('paid', self.child.membership_state)
        self.assertEqual(fields.Date.today(), self.child.membership_start)
        self.assertEqual(fields.Date.today(), self.child.membership_last_start)
        self.assertEqual(self.next_two_months, self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        self.partner.free_member = True
        self.assertEqual('free', self.child.membership_state)

    def test_category(self):
        line_one = self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': fields.Date.today(),
            'date_from': fields.Date.today(),
            'date_to': self.next_month,
            'partner': self.partner.id,
            'state': 'invoiced',
        })
        self.assertEqual(
            self.category_gold, self.partner.membership_category_ids,
        )
        self.assertEqual('Gold', self.partner.membership_categories)
        self.assertEqual(
            self.category_gold, self.child.membership_category_ids,
        )
        self.assertEqual('Gold', self.child.membership_categories)
        line_two = self.env['membership.membership_line'].create({
            'membership_id': self.silver_product.id,
            'member_price': 50.00,
            'date': fields.Date.today(),
            'date_from': fields.Date.today(),
            'date_to': self.next_two_months,
            'partner': self.partner.id,
            'state': 'paid',
        })
        self.assertEqual(
            self.category_gold + self.category_silver,
            self.partner.membership_category_ids,
        )
        self.assertTrue('Silver' in self.partner.membership_categories)
        self.assertTrue('Gold' in self.partner.membership_categories)
        self.assertEqual(
            self.category_gold + self.category_silver,
            self.child.membership_category_ids,
        )
        self.assertTrue('Silver' in self.child.membership_categories)
        self.assertTrue('Gold' in self.child.membership_categories)
        line_one.write({
            'state': 'canceled',
        })
        self.assertEqual(
            self.category_silver, self.partner.membership_category_ids,
        )
        self.assertEqual('Silver', self.partner.membership_categories)
        self.assertEqual(
            self.category_silver, self.child.membership_category_ids,
        )
        self.assertEqual('Silver', self.child.membership_categories)
        line_two.write({
            'state': 'waiting',
        })
        self.assertFalse(self.partner.membership_category_ids.ids)
        self.assertFalse(self.partner.membership_categories)
        self.assertFalse(self.child.membership_category_ids.ids)
        self.assertFalse(self.child.membership_categories)

    def test_remove_membership_line_with_invoice(self):
        account = self.partner.property_account_receivable_id.id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.today(),
            'account_id': self.partner.property_account_receivable_id.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': self.gold_product.id,
            'price_unit': 100.0,
            'name': 'Membership gold',
            'invoice_id': invoice.id,
            'quantity': 1.0,
            'account_id': account,
        })
        with self.assertRaises(UserError):
            self.partner.member_lines[0].unlink()
        invoice.invoice_line_ids.unlink()
        self.assertFalse(self.partner.member_lines)

    def test_membership_line_onchange(self):
        line = self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': fields.Date.today(),
            'partner': self.partner.id,
            'state': 'invoiced',
        })
        line._onchange_date()
        self.assertEqual(100.00, line.member_price)
        self.assertEqual(fields.Date.today(), line.date_from)
        self.assertEqual(self.next_month, line.date_to)
        line.write({
            'membership_id': self.silver_product.id,
        })
        line._onchange_membership_id()
        self.assertEqual(50, line.member_price)
        self.assertEqual(fields.Date.today(), line.date_from)
        self.assertEqual(self.next_two_months, line.date_to)

    def test_invoice(self):
        # This record has to be created here, or it will change other tests
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': fields.Date.today(),
            'type': 'out_invoice',
            'account_id': self.account_partner.id,
            'journal_id': self.journal.id,
            'invoice_line_ids': [
                (0, 0, {
                    'account_id': self.account_product.id,
                    'product_id': self.gold_product.id,
                    'price_unit': 100.0,
                    'name': self.gold_product.name,
                    'quantity': 1.0,
                }),
            ],
        })
        line = self.partner.member_lines[0]
        self.assertEqual('waiting', line.state)
        self.assertEqual(fields.Date.today(), line.date_from)
        self.assertEqual(self.next_month, line.date_to)
        invoice.action_invoice_open()  # validate invoice
        self.assertEqual('invoiced', line.state)
        invoice.pay_and_reconcile(self.bank_journal)  # pay invoice
        self.assertEqual('paid', line.state)
        self.env['account.payment'].search([
            ('partner_id', '=', self.partner.id)
        ]).cancel()
        invoice.action_invoice_cancel()
        self.assertEqual('canceled', line.state)
        invoice.action_invoice_draft()
        self.assertEqual('waiting', line.state)
        invoice.state = 'draft'  # HACK: Odoo resets this to open
        invoice.action_invoice_open()  # validate invoice
        self.assertEqual('invoiced', line.state)
        invoice.pay_and_reconcile(
            self.bank_journal, pay_amount=invoice.amount_total,
        )  # pay invoice
        self.assertEqual('paid', line.state)
        refund = invoice.refund()  # refund invoice
        refund.journal_id.update_posted = True
        refund.action_invoice_open()  # validate refund
        self.assertEqual('canceled', line.state)
        refund.action_invoice_cancel()
        self.assertEqual('paid', line.state)
        refund.action_cancel()
        refund.action_invoice_draft()
        refund.state = 'draft'  # HACK: Odoo resets this to open
        refund.invoice_line_ids[0].quantity = 0.5
        self.assertNotEqual(invoice.amount_untaxed, refund.amount_untaxed)
        refund.action_invoice_open()
        self.assertEqual('paid', line.state)

    def test_check_membership_all(self):
        self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': fields.Date.today(),
            'date_from': fields.Date.today(),
            'date_to': self.next_month,
            'partner': self.partner.id,
            'state': 'waiting',
        })
        # Force another state to check if the recomputation is done
        self.partner.membership_state = 'none'
        self.env['res.partner'].check_membership_all()
        self.assertEqual(self.partner.membership_state, 'waiting')

    def test_check_membership_expiry(self):
        self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': self.yesterday,
            'date_from': self.yesterday,
            'date_to': self.yesterday,
            'partner': self.partner.id,
            'state': 'waiting',
        })
        self.env['res.partner']._cron_update_membership()
        self.assertEqual(self.partner.membership_state, 'none')

    def test_unlink(self):
        self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 0,
            'partner': self.partner.id,
        })
        # We can't delete a partner with member lines
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.partner.unlink()
        # Create a brand new partner and delete it
        partner2 = self.env['res.partner'].create({
            'name': 'no member',
        })
        partner2.unlink()
        self.assertFalse(partner2.exists())

    def test_adhered_member(self):
        self.env['membership.membership_line'].create({
            'membership_id': self.gold_product.id,
            'member_price': 100.00,
            'date': fields.Date.today(),
            'date_from': fields.Date.today(),
            'date_to': self.next_month,
            'partner': self.partner.id,
            'state': 'waiting',
        })
        self.child.is_adhered_member = True
        self.child.membership_start_adhered = '2018-01-26'
        self.assertEqual(self.child.membership_start, '2018-01-26')
        self.child.associate_member = False
        self.child.onchange_associate_member()
        self.assertFalse(self.child.is_adhered_member)
