# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from datetime import datetime, date, time, timedelta
import math


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    membership_lines = fields.One2many(
        comodel_name='membership.membership_line',
        inverse_name='account_invoice_line')
        
    @api.model
    def create(self, vals):
        rec_line = super(AccountInvoiceLine, self).create(vals)
        if (rec_line.invoice_id.type == 'out_invoice' and 
                rec_line.product_id.membership and
                rec_line.product_id.membership_type == 'variable'):
            membership_vals = rec_line._prepare_membership_line()
            sm_id = rec_line.membership_lines.id   # Always return one record 
            rec_line.membership_lines = [(1, sm_id, membership_vals)]
        return rec_line

    @api.multi
    def write(self, vals):
        """Create before the lines of membership with variable period."""
        rec_memb_lines = self.env['membership.membership_line']
        if any(x in vals for x in ['product_id', 'quantity', 'invoice_id']):
            value = {}
            if vals.get('product_id'): 
                value.update({'product_id': vals.get('product_id')})
            if vals.get('quantity'):
                value.update({'quantity': vals.get('quantity')})
            # Get all edit records in account.invoice.line
            for rec_line in self: rec_memb_lines |= rec_line.membership_lines
            rec_memb_lines.write({'membership_lines': value})
        return super(AccountInvoiceLine, self).write(vals)

    @api.multi
    def _prepare_membership_line(self):
        rec_prod_templ = self.product_id.product_tmpl_id
        rec_invoice = self.invoice_id
        rec_memb_line = self._get_last_membership()
        if rec_memb_line.exists() and rec_memb_line.date_to:
            date_to = rec_memb_line.date_to
            date_from = fields.Date.from_string(date_to) + timedelta(days=1)
        else:
            date_from = fields.Date.from_string(rec_invoice.date_invoice 
                                                or fields.Date.today())
        date_to = rec_prod_templ._get_next_date(date_from)-timedelta(days=1)
        return {
            'partner': self.invoice_id.partner_id.id,
            'membership_id': self.product_id.id,
            'member_price': self.price_unit,
            'date': fields.Date.today(),
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
            'state': 'waiting',
            'account_invoice_line': self.id,
        }

    @api.multi
    def _get_last_membership(self):
        rec_invoice = self.invoice_id
        rec_memb_line = self.env['membership.membership_line']
        args = [('partner', '=', rec_invoice.partner_id.id), 
                ('state', 'not in', ['none', 'canceled'])]
        order = "date_to desc"
        return rec_memb_line.search(args, limit=1, order=order)
