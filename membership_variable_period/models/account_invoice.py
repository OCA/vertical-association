# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, fields
from datetime import timedelta
import math


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    membership_lines = fields.One2many(
        comodel_name='membership.membership_line',
        inverse_name='account_invoice_line')

    def _prepare_membership_line(self, invoice, product, price_unit, line_id,
                                 memb_lines=False):
        if memb_lines and memb_lines[0].date_to:
            date_from = (fields.Date.from_string(memb_lines[0].date_to) +
                         timedelta(days=1))
        else:
            date_from = fields.Date.from_string(
                invoice.date_invoice or fields.Date.today())
        date_to = (product.product_tmpl_id._get_next_date(date_from) -
                   timedelta(days=1))
        return {
            'partner': invoice.partner_id.id,
            'membership_id': product.id,
            'member_price': price_unit,
            'date': invoice.date_invoice or fields.Date.today(),
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
            'state': 'waiting',
            'account_invoice_line': line_id,
        }

    def _membership_line_extra_create(self, qty, invoice, line, price_unit):
        memb_line_model = self.env['membership.membership_line']
        for i in range(qty):
            memb_lines = memb_line_model.search(
                [('account_invoice_line', '=', line.id),
                 ('state', 'not in', ['none', 'canceled'])],
                order="date_to desc")
            membership_vals = self._prepare_membership_line(
                invoice, line.product_id, price_unit, line.id, memb_lines)
            memb_line_model.create(membership_vals)

    @api.multi
    def write(self, vals):
        """Create before the lines of membership with variable period."""
        memb_line_model = self.env['membership.membership_line']
        if any(x in vals for x in ['product_id', 'quantity', 'invoice_id']):
            for line in self:
                product = (
                    self.env['product.product'].browse(vals['product_id']) if
                    vals.get('product_id') else line.product_id)
                invoice = (
                    self.env['account.invoice'].browse(vals['invoice_id']) if
                    vals.get('invoice_id') else line.invoice_id)
                if (invoice.type == 'out_invoice' and
                        product.membership and
                        product.membership_type == 'variable'):
                    quantity = vals.get('quantity', line.quantity)
                    quantity = int(math.ceil(quantity))
                    price_unit = vals.get('price_unit', line.price_unit)
                    memb_lines = memb_line_model.search(
                        [('account_invoice_line', '=', line.id),
                         ('state', 'not in', ['none', 'canceled'])],
                        order="date desc, id desc")
                    # Invoice date or product changed
                    if (memb_lines and (
                            invoice.date_invoice != memb_lines[-1].date_from or
                            product.id != memb_lines[-1].membership_id.id)):
                        if len(memb_lines) > 1:
                            # Remove all except last one
                            memb_lines[:-1].unlink()
                        # Update with changes
                        membership_vals = self._prepare_membership_line(
                            invoice, product, price_unit, line.id)
                        memb_lines[0].write(membership_vals)
                    # Qty changed
                    if len(memb_lines) < quantity:
                        # Add missing membership lines
                        missing_number = quantity - len(memb_lines)
                        self._membership_line_extra_create(
                            missing_number, invoice, line, price_unit)
                    elif len(memb_lines) > quantity:
                        # Remove extra membership lines
                        extra_number = len(memb_lines) - quantity
                        memb_lines[:extra_number].unlink()
                    else:
                        # Update data of current membership line
                        membership_vals = self._prepare_membership_line(
                            invoice, product, price_unit, line.id)
                        memb_lines[0].write(membership_vals)
        return super(AccountInvoiceLine, self).write(vals)

    @api.model
    def create(self, vals):
        price_unit = vals.get('price_unit', 0.0)
        line = super(AccountInvoiceLine, self).create(vals)
        if (line.invoice_id.type == 'out_invoice' and
                line.product_id.membership and
                line.product_id.membership_type == 'variable'):
            membership_vals = self._prepare_membership_line(
                line.invoice_id, line.product_id, price_unit, line.id)
            # There's already the super line
            line.membership_lines[0].write(membership_vals)
            qty = int(line.quantity)
            if qty > 1:
                # Create more membership lines if qty > 1
                self._membership_line_extra_create(
                    qty - 1, line.invoice_id, line, price_unit)
        return line
