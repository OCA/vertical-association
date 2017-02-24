# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingenieria S.L. - Pedro M. Baeza
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    @api.model
    def create(self, vals):
        rec_invoice_line = super(AccountInvoiceLine, self).create(vals)
        if not vals.get('product_id'): return rec_invoice_line
        rec_product = self.env['product.product'].browse(vals.get('product_id'))
        if not rec_product.membership or rec_product.initial_fee == 'none':
            return rec_invoice_line
        # See if this is the first invoice
        args = [('partner_id', '=', rec_invoice_line.invoice_id.partner_id.id),
                ('state', 'in', ('draft', 'open', 'paid')), 
                ('type', '=', 'out_invoice'),
                ('id', '!=', rec_invoice_line.invoice_id.id),
                ('invoice_line_ids.product_id', '=', rec_product.id)]
        rec_invoice = self.env['account.invoice'].search(args)
        all_prods = rec_invoice.mapped('invoice_line_ids').mapped('product_id')
        if not rec_invoice.exists():
            # Charge initial fee
            rec_fee = self.create(rec_invoice_line._prepare_initial_fee_vals())
#            rec_fee._set_taxes()
        return rec_invoice_line

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

