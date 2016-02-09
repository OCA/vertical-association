# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from openerp import fields
from openerp.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super(TestResPartner, self).setUp()
        self.next_two_months = fields.Date.to_string(
            fields.Date.from_string(fields.Date.today()) + timedelta(days=60))
        self.next_month = fields.Date.to_string(
            fields.Date.from_string(fields.Date.today()) + timedelta(days=30))
        self.category = self.env.ref('membership_extra_info.category_gold')
        self.reason = self.env.ref('membership_extra_info.reason_unsatisfied')
        self.partner = self.env.ref('base.res_partner_25')
        self.child = self.env.ref('base.res_partner_15')
        self.child.associate_member = self.partner.id
        self.wizard_form = self.env.ref('membership_extra_info.'
                                        'decline_reason_wizard_form')
        self.product = self.env['product.product'].create({
            'type': 'service',
            'name': 'Membership 2005',
            'membership': True,
            'membership_date_from': '2005-02-01',
            'membership_date_to': self.next_two_months,
            'membership_category': self.category.id,
            'list_price': 100.00,
        })
        self.product_old_01 = self.env['product.product'].create({
            'type': 'service',
            'name': 'Membership 2001',
            'membership': True,
            'membership_date_from': '2001-01-01',
            'membership_date_to': '2001-12-31',
            'membership_category': self.category.id,
            'list_price': 75.00,
        })
        self.product_old_02 = self.env['product.product'].create({
            'type': 'service',
            'name': 'Membership 2002',
            'membership': True,
            'membership_date_from': '2002-01-01',
            'membership_date_to': '2002-12-31',
            'membership_category': self.category.id,
            'list_price': 85.00,
        })
        self.product_old_03 = self.env['product.product'].create({
            'type': 'service',
            'name': 'Membership 2003',
            'membership': True,
            'membership_date_from': '2003-01-01',
            'membership_date_to': '2003-12-31',
            'membership_category': self.category.id,
            'list_price': 95.00,
        })
        self.line_old_01 = self.env['membership.membership_line'].create({
            'membership_id': self.product_old_01.id,
            'member_price': 75.00,
            'date': '2001-01-01',
            'date_from': '2001-01-01',
            'date_to': '2001-12-31',
            'partner': self.partner.id,
            'state': 'paid',
        })
        self.line_old_02 = self.env['membership.membership_line'].create({
            'membership_id': self.product_old_02.id,
            'member_price': 85.00,
            'date': '2002-01-01',
            'date_from': '2002-01-01',
            'date_to': '2002-12-31',
            'partner': self.partner.id,
            'state': 'paid',
        })
        self.line_old_03 = self.env['membership.membership_line'].create({
            'membership_id': self.product_old_03.id,
            'member_price': 95.00,
            'date': '2003-01-01',
            'date_from': '2003-01-01',
            'date_to': '2003-12-31',
            'partner': self.partner.id,
            'state': 'canceled',
        })
        self.line = self.env['membership.membership_line'].create({
            'membership_id': self.product.id,
            'member_price': 100.00,
            'date': '2005-02-01',
            'date_from': '2005-02-01',
            'date_to': self.next_two_months,
            'partner': self.partner.id,
            'state': 'invoiced',
        })
        self.wizard = self.env['membership.decline_reason_wizard'].create({
            'membership_line_id': self.line.id,
            'date_decline': fields.Date.today(),
            'date_to': self.next_month,
            'decline_reason': self.reason.id,
        })

    def test_01_partner(self):
        self.assertEqual(self.partner.membership_last_start,
                         self.line.date_from)
        self.assertEqual(self.partner.membership_last_decline_reason.id,
                         self.line.decline_reason.id)
        self.assertEqual(self.partner.membership_last_decline_date,
                         self.line.date_decline)
        self.assertEqual(self.partner.membership_last_category.id,
                         self.line.category.id)
        self.assertEqual(self.child.membership_last_start,
                         self.partner.membership_last_start)
        self.assertEqual(self.child.membership_last_decline_reason,
                         self.partner.membership_last_decline_reason)
        self.assertEqual(self.child.membership_last_decline_date,
                         self.partner.membership_last_decline_date)
        self.assertEqual(self.child.membership_last_category.id,
                         self.partner.membership_last_category.id)

    def test_02_compute_show_decline_button(self):
        self.assertFalse(self.line.show_decline_button)
        self.assertFalse(self.line_old_01.show_decline_button)
        self.assertFalse(self.line_old_02.show_decline_button)
        self.assertFalse(self.line_old_03.show_decline_button)
        self.line.state = 'paid'
        self.assertTrue(self.line.show_decline_button)

    def test_03_button_decline(self):
        self.line.state = 'paid'
        action = self.line.button_decline()
        self.assertEqual(action.get('type'), 'ir.actions.act_window')
        self.assertEqual(action.get('view_id'), self.wizard_form.id)
        self.assertEqual(action.get('target'), 'new')
        self.assertEqual(action.get('res_model'),
                         'membership.decline_reason_wizard')
        context = action.get('context')
        self.assertEqual(context.get('default_membership_line_id'),
                         self.line.id)
        self.assertEqual(context.get('default_date_decline'),
                         fields.Date.today())
        self.assertEqual(context.get('default_date_to'),
                         fields.Date.today())

    def test_04_decline(self):
        self.wizard.decline()
        self.assertEqual(self.line.decline_reason.id,
                         self.wizard.decline_reason.id)
        self.assertEqual(self.line.date_decline,
                         self.wizard.date_decline)
        self.assertEqual(self.line.date_to, self.wizard.date_to)
        self.assertEqual(self.partner.membership_stop,
                         self.wizard.date_to)
        self.assertEqual(self.partner.membership_last_decline_reason.id,
                         self.wizard.decline_reason.id)
        self.assertEqual(self.partner.membership_last_decline_date,
                         self.wizard.date_decline)
        self.assertEqual(self.child.membership_stop,
                         self.partner.membership_stop)
        self.assertEqual(self.child.membership_last_decline_reason.id,
                         self.partner.membership_last_decline_reason.id)
        self.assertEqual(self.child.membership_last_decline_date,
                         self.partner.membership_last_decline_date)
