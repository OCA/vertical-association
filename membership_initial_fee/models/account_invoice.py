# Copyright 2015-2020 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models
from odoo.tools.translate import _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _prepare_initial_fee_vals(self):
        self.ensure_one()
        product = self.product_id
        product_fee = self.product_id.product_fee
        line_vals = {
            'product_id': product_fee.id,
            'quantity': 1.0,
            'invoice_id': self.invoice_id.id,
            'account_analytic_id': self.account_analytic_id.id,
        }
        inv_line = self.env['account.invoice.line'].new(line_vals)
        inv_line._onchange_product_id()
        inv_line.name = (product_fee.description_sale or
                         _('Membership initial fee'))
        if product.initial_fee == 'fixed':
            inv_line.price_unit = product.fixed_fee
        elif product.initial_fee == 'percentage':
            inv_line.price_unit = (
                product.percentage_fee * self.price_unit / 100
            )
        return inv_line._convert_to_write(inv_line._cache)

    @api.multi
    def initial_fee_create_check(self, product=False):
        """
        Inherit this method to implement a custom method
        to decide whether or not to create the initial fee

        :param product:
        :return:
        """
        # TODO: remove product parameter in v12
        product = product or self.product_id
        if (not product or not product.membership or
                product.initial_fee == 'none' or
                self.invoice_id.type != "out_invoice"):
            return False
        # If we are associated to another partner membership, evaluate that
        # partner lines
        partner = (
            self.partner_id.associate_member or self.invoice_id.partner_id)
        # By default, partner to check is the partner of the invoice, but
        # if a special method is found, overwritten in other modules, then
        # the partner is got from that method
        if hasattr(self,
                   '_get_partner_for_membership'):  # pragma: no cover
            partner = self._get_partner_for_membership()
        # See if partner has any membership line to decide whether or not
        # to create the initial fee
        return not self.env['membership.membership_line'].search_count([
            ('partner', '=', partner.id),
            ('account_invoice_line', 'not in', (self.id,)),
            ('state', 'not in', ['none', 'canceled']),
        ])

    @api.model
    def create(self, vals):
        invoice_line = super(AccountInvoiceLine, self).create(vals)
        if invoice_line.initial_fee_create_check():
            # Charge initial fee
            self.create(invoice_line._prepare_initial_fee_vals())
        return invoice_line
