# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
from dateutil.relativedelta import relativedelta
from openerp import fields, exceptions
from openerp.tests.common import TransactionCase


class TestMembershipAutoextend(TransactionCase):
    def invoice_membership(self, partner, membership_product, extra_days=0):
        # write today - delay to make this extension trigger a warning
        # email to the partner
        invoice_date = datetime.date.today() - relativedelta(
            days=extra_days,
            years=membership_product.membership_interval_qty
        )
        invoice_ids = partner\
            .with_context(
                default_date_invoice=fields.Date.to_string(invoice_date))\
            .create_membership_invoice(
                product_id=membership_product.id, datas={
                    'amount': membership_product.list_price,
                })
        invoice = self.env['account.invoice'].browse(invoice_ids)
        try:
            self.env['account.fiscalyear'].finds(fields.Date.to_string(
                invoice_date))
        except exceptions.RedirectWarning:
            self.env['account.fiscalyear'].create({
                'name': str(invoice_date.year),
                'code': str(invoice_date.year),
                'date_start': fields.Date.to_string(
                    invoice_date + relativedelta(month=1, day=1)
                ),
                'date_stop': fields.Date.to_string(
                    invoice_date + relativedelta(month=12, day=31)
                ),
            })
        try:
            self.env['account.period'].find(dt=fields.Date.to_string(
                invoice_date))
        except exceptions.RedirectWarning:
            self.env['account.period'].create({
                'name': '%02d' % invoice_date.month,
                'date_start': fields.Date.to_string(
                    invoice_date + relativedelta(day=1)
                ),
                'date_stop': fields.Date.to_string(
                    invoice_date + relativedelta(months=1, day=1, days=-1)
                ),
                'fiscalyear_id': self.env['account.fiscalyear'].finds(
                    dt=fields.Date.to_string(invoice_date))[0],
            })

        invoice.write({
            'date_invoice': fields.Date.to_string(invoice_date),
        })
        invoice.signal_workflow('invoice_open')
        return invoice

    def test_membership_autoextend(self):
        membership_product = self.env.ref(
            'membership_autoextend.product_autoextend_membership')
        partner = self.env.ref('base.res_partner_address_4')
        self.invoice_membership(
            partner, membership_product,
            extra_days=membership_product.membership_autoextend_warning_days -
            1
        )
        self.assertEqual(partner.membership_state, 'old')

        partner = self.env.ref('base.res_partner_address_3')
        self.invoice_membership(partner, membership_product)
        self.assertEqual(partner.membership_state, 'old')

        # now see what your cronjob makes of this
        self.env['res.partner'].check_membership_expiry()
        # our first partner must have gotten an email
        partner = self.env.ref('base.res_partner_address_4')
        self.assertTrue(
            self.env['mail.message'].search([
                ('res_id', 'in', partner.member_lines.ids),
                ('model', '=', partner.member_lines._name),
                (
                    'subject', '=',
                    self.env.ref(
                        'membership_autoextend.'
                        'email_template_autoextend_warning'
                    ).subject
                ),
            ])
        )
        # the second one must hasve gotten another mail and be extended
        partner = self.env.ref('base.res_partner_address_3')
        self.assertTrue(
            self.env['mail.message'].search([
                ('res_id', 'in', partner.member_lines.ids),
                ('model', '=', partner.member_lines._name),
                (
                    'subject', '=', self.env.ref(
                        'membership_autoextend.'
                        'email_template_autoextend_info').subject
                ),
            ])
        )
        self.assertEqual(partner.membership_state, 'invoiced')
