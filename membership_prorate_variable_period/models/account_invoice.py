# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, exceptions, models
from odoo.tools import date_utils


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
                _("It's not possible to prorate daily periods."))
        if product.membership_interval_unit == 'weeks':
            date_from = date_utils.start_of(date, 'week')
        elif product.membership_interval_unit == 'months':
            date_from = date_utils.start_of(date, 'month')
        elif product.membership_interval_unit == 'years':
            date_from = date_utils.start_of(date, 'year')
        date_to = date_utils.subtract(product._get_next_date(date), days=1)
        return date_from, date_to
