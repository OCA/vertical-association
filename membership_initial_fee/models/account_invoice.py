# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Pedro M. Baeza
# © 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, vals):
        rec_invoice = super(AccountInvoiceLine, self).create(vals)
        product = self.env['product.product'].browse(vals['product_id'])
        if not product.membership or product.initial_fee == 'none':
            return rec_invoice
        # See if this is the first invoice
        invoices = self.env['account.invoice'].search(
            [('partner_id', '=', rec_invoice.invoice_id.partner_id.id),
             ('state', 'in', ('draft', 'open', 'paid')),
             ('invoice_line_ids.product_id', '=', product.id)])
        if len(invoices) == 1:
            # Charge initial fee
            self.create(rec_invoice._prepare_initial_fee_vals())
        return rec_invoice

    @api.multi
    def _prepare_initial_fee_vals(self):
        rec_prod_fee = self.product_id.product_fee or False
        if not rec_prod_fee.exists(): return False
        if self.product_id.initial_fee == 'fixed':
            price = self.product_id.fixed_fee
        elif self.product_id.initial_fee == 'percentage':
            price = self.product_id.percentage_fee * self.price_unit / 100
        account_id = rec_prod_fee.property_account_income_id and \
                        rec_prod_fee.property_account_income_id.id or \
                            self.product_id.property_account_income_id.id
        line_vals = {
            'name' : _('Membership initial fee'),
            'product_id': self.product_id.product_fee.id,
            'invoice_id': self.invoice_id.id,
            'account_analytic_id': self.account_analytic_id.id,
            'price_unit': price,
            'account_id': account_id or False
        }
        return line_vals
