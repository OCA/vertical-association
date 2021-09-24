# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_category_id = fields.Many2one(
        string="Membership category",
        comodel_name="membership.membership_category",
        compute="_compute_membership_category_id",
        readonly=False,
        store=True,
    )

    def _get_next_date(self, date, qty=1):
        self.ensure_one()
        if self.membership_date_to:
            date_to = fields.Date.from_string(self.membership_date_to)
            return date_to + timedelta(1)
        return False  # pragma: no cover

    @api.depends("company_id")
    def _compute_membership_category_id(self):
        """Reset the Membership Category in case a different Company is set"""
        for record in self:
            if record.company_id and record.membership_category_id.company_id:
                if record.membership_category_id.company_id != record.company_id:
                    record.membership_category_id = False
