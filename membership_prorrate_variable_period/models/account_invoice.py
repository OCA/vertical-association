# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, exceptions, fields, models, _
from datetime import datetime, date, time, timedelta


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _get_membership_interval(self):
        """Get the interval to evaluate as the theoretical membership period.
        :param product: Product that defines the membership
        :param date: date object for the requested date to determine
        the variable period
        :return: A tuple with 2 date objects with the beginning and the
        end of the period
        """
        date = datetime.now()
        if self.product_id.membership_type == 'fixed':
            return super(AccountInvoiceLine, self)._get_membership_interval()
        if self.product_id.membership_interval_unit == 'days':
            raise exceptions.Warning(
                _("It's not possible to prorrate daily periods."))
        if self.product_id.membership_interval_unit == 'weeks':
            weekday = date.weekday()
            date_from = date - datetime.timedelta(weekday)
        elif self.product_id.membership_interval_unit == 'months':
            date_from = datetime(year=date.year, month=date.month, day=1).date()
        elif self.product_id.membership_interval_unit == 'years':
            date_from = datetime(year=date.year, month=1, day=1).date()
        next_date = self.product_id.product_tmpl_id._get_next_date(date)
        date_to = next_date - timedelta(1)
        return date_from, date_to

