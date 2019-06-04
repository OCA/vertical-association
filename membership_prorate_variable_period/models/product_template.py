# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import math
from odoo import _, api, exceptions, models
from odoo.tools import date_utils


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def _get_next_date(self, date, qty=1):
        next_date = super(ProductTemplate, self)._get_next_date(date)
        if self.membership_interval_unit == 'days':
            raise exceptions.Warning(
                _("It's not possible to prorate daily periods."))
        qty = math.ceil(qty) * self.membership_interval_qty
        if self.membership_interval_unit == 'weeks':
            next_date = date_utils.start_of(date, 'week')
            next_date = date_utils.add(next_date, weeks=qty)
        elif self.membership_interval_unit == 'months':
            next_date = date_utils.start_of(date, 'month')
            next_date = date_utils.add(next_date, months=qty)
        elif self.membership_interval_unit == 'years':
            next_date = date_utils.start_of(date, 'year')
            next_date = date_utils.add(next_date, years=qty)
        return next_date
