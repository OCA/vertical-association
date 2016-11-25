# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_category_id = fields.Many2one(
        string="Membership category",
        comodel_name='membership.membership_category')

    @api.multi
    def _get_next_date(self, date, qty=1):
        self.ensure_one()
        if self.membership_date_to:
            date_to = fields.Date.from_string(self.membership_date_to)
            return date_to + timedelta(1)
        return False
