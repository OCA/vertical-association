# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingenieria S.L. - Pedro M. Baeza
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from datetime import datetime, date, time, timedelta


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, vals):
        rec_invoice_line = super(AccountInvoiceLine, self).create(vals)
        if not vals.get('product_id'): return rec_invoice_line
        rec_product = self.env['product.product'].browse(vals.get('product_id'))
        if not rec_product.membership or not rec_product.membership_prorrate:
            return rec_invoice_line
        # Change quantity accordingly the prorrate and update vals
        line_vals = rec_invoice_line._prepare_invoice_line_prorrate_vals()
        if line_vals: 
            rec_invoice_line.write(line_vals)
            # Rectify membership price and start date in this case
            price = rec_invoice_line.price_subtotal
            date_invoice = rec_invoice_line._get_updated_invoice_date()
            rec_memb_line = self.env['membership.membership_line']
            args = [('account_invoice_line', '=', rec_invoice_line.id)]
            rec_memb_line.search(args, limit=1)
            rec_memb_line.write({'member_price': price, 
                                 'date_from': date_invoice})
        return rec_invoice_line

    @api.multi
    def _prepare_invoice_line_prorrate_vals(self):
        res = {}
        date_from, date_to = self._get_membership_interval() 
        theoretical_duration = date_to - date_from + timedelta(1)
        real_duration = date_to - self._get_updated_invoice_date()
        if theoretical_duration != real_duration:
            res = {'quantity': round(float(real_duration.days) / 
                                      theoretical_duration.days, 2)}
        return res
    
    @api.multi
    def _get_updated_invoice_date(self):
        """Get invoice date to update."""
        date_invoice = fields.Date.from_string(self.invoice_id.date_invoice \
                                               or fields.Date.today())
        date_from, date_to = self._get_membership_interval()
        date_invoice = date_from if date_invoice < date_from else date_invoice
        date_invoice = date_to if date_invoice > date_to else date_invoice
        return date_invoice          

    @api.multi
    def _get_membership_interval(self):
        """Get the interval to evaluate as the theoretical membership period.
        :param product: Product that defines the membership
        :param date: date object for the requested date (if needed for
        inherited computations)
        :return: A tuple with 2 date objects with the beginning and 
        the end of the period
        """
        date_from = self.product_id.membership_date_from or fields.Date.today()
        date_from_str = fields.Date.from_string(date_from)
        date_to = self.product_id.membership_date_to or fields.Date.today()
        date_to_str = fields.Date.from_string(date_to)
        return date_from_str, date_to_str



