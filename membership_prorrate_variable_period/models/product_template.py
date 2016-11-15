# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, exceptions, api, _
import datetime
import calendar


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def _get_next_date(self, date):
        res = super(ProductTemplate, self)._get_next_date(date)
        if self.membership_interval_qty != 1:
            raise exceptions.Warning(
                _("It's not possible to prorrate periods which interval "
                  "quantity is different from 1."))
        if self.membership_interval_unit == 'days':
            raise exceptions.Warning(
                _("It's not possible to prorrate daily periods."))
        if self.membership_interval_unit == 'weeks':
            weekday = date.weekday()
            date_from = date - datetime.timedelta(weekday)
            res = date_from + datetime.timedelta(7)
        elif self.membership_interval_unit == 'months':
            last_month_day = calendar.monthrange(
                date.year, date.month)[1]
            res = (datetime.date(
                day=last_month_day, month=date.month, year=date.year) +
                datetime.timedelta(1))
        elif self.membership_interval_unit == 'years':
            res = (datetime.date(day=31, month=12, year=date.year) +
                   datetime.timedelta(1))
        return res
