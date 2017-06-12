# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, fields
from datetime import timedelta


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _get_membership_interval(self, product, date):
        """Get the interval to evaluate as the theoretical membership period.
        :param product: Product that defines the membership
        :param date: date object for the requested date (if needed for
        inherited computations)
        :return: A tuple with 2 date objects with the beginning and the
        end of the period
        """
        date_from = fields.Date.from_string(product.membership_date_from)
        date_to = fields.Date.from_string(product.membership_date_to)
        return date_from, date_to

    def _prepare_invoice_line_prorrate_vals(self, invoice_line):
        product = invoice_line.product_id
        date_invoice = fields.Date.from_string(
            invoice_line.invoice_id.date_invoice or fields.Date.today())
        date_from, date_to = self._get_membership_interval(
            product, date_invoice)
        date_invoice = date_from if date_invoice < date_from else date_invoice
        date_invoice = date_to if date_invoice > date_to else date_invoice
        theoretical_duration = date_to - date_from + timedelta(1)
        real_duration = date_to - date_invoice
        if theoretical_duration != real_duration:
            return {
                'quantity': round(float(real_duration.days) /
                                  theoretical_duration.days, 2),
                'date_from': date_invoice,
            }

    @api.model
    def create(self, vals):
        invoice_line = super(AccountInvoiceLine, self).create(vals)
        product = self.env['product.product'].browse(
            vals.get('product_id', False)
        )
        if not product.membership or not product.membership_prorrate:
            return invoice_line
        # Change quantity accordingly the prorrate
        invoice_line_vals = self._prepare_invoice_line_prorrate_vals(
            invoice_line)
        if invoice_line_vals:
            date_from = invoice_line_vals.pop('date_from')
            invoice_line.write(invoice_line_vals)
            # Rectify membership price and start date in this case
            memb_line = self.env['membership.membership_line'].search(
                [('account_invoice_line', '=', invoice_line.id)], limit=1)
            memb_line.write({'member_price': invoice_line.price_subtotal,
                             'date_from': date_from})
        return invoice_line
