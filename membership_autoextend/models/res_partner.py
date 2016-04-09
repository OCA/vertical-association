# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    membership_autoextend_opt_out = fields.Boolean(
        'Opt out of autoextension', default=False)
    membership_autoextend = fields.Boolean(related=[
        'membership_current', 'membership_id', 'membership_autoextend',
    ])
    membership_current = fields.Many2one(
        'membership.membership_line', string='Current membership',
        compute='_compute_membership_current',
        search='_search_membership_current')

    @api.multi
    def _compute_membership_current(self):
        today = fields.Date.today()
        for this in self:
            for membership in this.member_lines:
                if membership.date_from and membership.date_from > today:
                    continue
                if membership.date_to and membership.date_to < today:
                    continue
                this.membership_current = membership

    @api.model
    def _search_membership_current(self, operator, value):
        self.env.cr.execute(
            "select l.id from res_partner p "
            "join membership_membership_line l on l.partner=p.id "
            "and l.date_from <= now() and l.date_to >= now()")
        return [
            '&',
            ('member_lines', 'in', [i for i, in self.env.cr.fetchall()]),
            ('member_lines', operator, value)
        ]

    @api.model
    def check_membership_expiry(self):
        result = super(ResPartner, self).check_membership_expiry()
        today = fields.Date.from_string(fields.Date.context_today(self))
        for this in self.search([
            ('membership_state', 'in', ['paid', 'old', 'waiting', 'invoiced']),
            ('membership_autoextend_opt_out', '=', False),
        ]):
            membership = this.membership_current or this.member_lines[-1:]
            product = membership.membership_id
            if not product.membership_autoextend:
                continue
            date_to = fields.Date.from_string(membership.date_to)
            if product.membership_autoextend_warning_days and\
                    product.membership_autoextend_warning_template_id and\
                    (
                        today - date_to
                    ).days == product.membership_autoextend_warning_days:
                product.membership_autoextend_warning_template_id.send_mail(
                    membership.id)
            if fields.Date.from_string(this.membership_stop) <= today:
                extension_product = \
                    product.membership_autoextend_product_id or product
                invoice_ids = this.create_membership_invoice(
                    extension_product.id, datas={
                        'amount': extension_product.list_price,
                    })
                self.env['account.invoice'].browse(invoice_ids)\
                    .signal_workflow('invoice_open')
                if product.membership_autoextend_info_template_id:
                    product.membership_autoextend_info_template_id.send_mail(
                        this.membership_current.id)
        return result and True
