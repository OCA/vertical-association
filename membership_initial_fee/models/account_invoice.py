# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _prepare_initial_fee_vals(self, invoice_line):
        product = invoice_line.product_id
        product_fee = invoice_line.product_id.product_fee
        line_vals = {
            'product_id': product_fee.id,
            'quantity': 1.0,
            'invoice_id': invoice_line.invoice_id.id,
            'account_analytic_id': invoice_line.account_analytic_id.id,
        }
        inv_line = self.env['account.invoice.line'].new(line_vals)
        inv_line._onchange_product_id()
        inv_line.name = _('Membership initial fee')
        if product.initial_fee == 'fixed':
            inv_line.price_unit = product.fixed_fee
        elif product.initial_fee == 'percentage':
            inv_line.price_unit = (
                product.percentage_fee * invoice_line.price_unit / 100
            )
        return inv_line._convert_to_write(inv_line._cache)

    @api.model
    def initial_fee_create_check(self, product, invoice_line):
        """Inherit this method to implement a custom method
           to decide whether or not to create the initial fee
        """
        if not product.membership or product.initial_fee == 'none':
            return False
        # By default, partner to check is the partner of the invoice, but
        # if a special method is found, overwritten in other modules, then
        # the partner is got from that method
        partner = invoice_line.invoice_id.partner_id
        if hasattr(invoice_line,
                   '_get_partner_for_membership'):  # pragma: no cover
            partner = invoice_line._get_partner_for_membership()
        # See if partner has any membership line
        member_lines = self.env['membership.membership_line'].search([
            ('partner', '=', partner.id),
            ('account_invoice_line', 'not in', (invoice_line.id, )),
            ('state', 'not in', ['none', 'canceled']),
        ])
        return not bool(member_lines)

    @api.model
    def create(self, vals):
        invoice_line = super(AccountInvoiceLine, self).create(vals)
        product = self.env['product.product'].browse(
            vals.get('product_id'))
        if self.initial_fee_create_check(product, invoice_line):
            # Charge initial fee
            self.create(self._prepare_initial_fee_vals(invoice_line))
        return invoice_line
