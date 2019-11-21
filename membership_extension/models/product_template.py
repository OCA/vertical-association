# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_category_id = fields.Many2one(
        string="Membership category",
        comodel_name='membership.membership_category',
    )

    @api.multi
    def _get_next_date(self, date, qty=1):
        self.ensure_one()
        if self.membership_date_to:
            date_to = fields.Date.from_string(self.membership_date_to)
            return date_to + timedelta(1)
        return False  # pragma: no cover

    @api.onchange('company_id')
    def _onchange_company_id_compute_membership_category_id(self):
        """Reset the Membership Category in case a different Company is set"""
        category_company = self.membership_category_id.company_id
        if self.company_id and category_company:
            if category_company != self.company_id:
                self.membership_category_id = False
