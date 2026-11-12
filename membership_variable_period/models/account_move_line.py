# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019-2020 Onestein - Andrea Stirpe
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
import math
from datetime import timedelta

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_variable_period_product_membership_types(self):
        return ["variable"]

    def _prepare_membership_line_dates(self):
        """
        For the lines configured with a proper product, apply the logics of flexible
        period when computing `date_to`
        """
        product_tmpl = self.product_id.product_tmpl_id
        membership_types = self._get_variable_period_product_membership_types()
        if product_tmpl.membership_type not in membership_types:
            return super()._prepare_membership_line_dates()
        qty = int(math.ceil(self.quantity))
        date_from = self.move_id.invoice_date or fields.Date.context_today(self)
        date_to = product_tmpl._get_next_date(date_from, qty=qty)
        date_to = date_to and (date_to - timedelta(days=1)) or False
        return (date_from, date_to)
