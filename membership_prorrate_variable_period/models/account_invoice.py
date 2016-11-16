# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, exceptions, _
import datetime


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _get_membership_interval(self, product, date):
        """Get the interval to evaluate as the theoretical membership period.
        :param product: Product that defines the membership
        :param date: date object for the requested date to determine
        the variable period
        :return: A tuple with 2 date objects with the beginning and the
        end of the period
        """
        if product.membership_type == 'fixed':
            return super(AccountInvoiceLine, self)._get_membership_interval(
                product, date)
        if product.membership_interval_unit == 'days':
            raise exceptions.Warning(
                _("It's not possible to prorrate daily periods."))
        if product.membership_interval_unit == 'weeks':
            weekday = date.weekday()
            date_from = date - datetime.timedelta(weekday)
        elif product.membership_interval_unit == 'months':
            date_from = datetime.date(day=1, month=date.month, year=date.year)
        elif product.membership_interval_unit == 'years':
            date_from = datetime.date(day=1, month=1, year=date.year)
        date_to = product._get_next_date(date) - datetime.timedelta(1)
        return date_from, date_to
