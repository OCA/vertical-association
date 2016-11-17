# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import math
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from openerp import models, exceptions, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def _get_next_date(self, date, qty=1):
        res = super(ProductTemplate, self)._get_next_date(date)
        if self.membership_interval_unit == 'days':
            raise exceptions.Warning(
                _("It's not possible to prorrate daily periods."))
        qty = int(math.ceil(qty)) * self.membership_interval_qty
        if self.membership_interval_unit == 'weeks':
            weekday = date.weekday()
            date_from = date - datetime.timedelta(weekday)
            res = date_from + datetime.timedelta(7 * qty)
        elif self.membership_interval_unit == 'months':
            date_to = date
            if qty > 1:
                date_to += relativedelta(months=(qty - 1))
            last_month_day = calendar.monthrange(
                date_to.year, date_to.month)[1]
            res = (datetime.date(
                day=last_month_day, month=date_to.month, year=date_to.year) +
                datetime.timedelta(1))
        elif self.membership_interval_unit == 'years':
            date_to = date
            if qty > 1:
                date_to += relativedelta(years=(qty - 1))
            res = (datetime.date(day=31, month=12, year=date_to.year) +
                   datetime.timedelta(1))
        return res
