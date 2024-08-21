# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MembershipCategory(models.Model):
    _name = "membership.membership_category"
    _description = "Membership category"

    name = fields.Char(required=True, translate=True)
    company_id = fields.Many2one("res.company")

    @api.constrains("company_id")
    def _check_company_id(self):
        if self.env.context.get("bypass_company_validation"):
            return
        categories = self.filtered(lambda c: c.company_id)
        templates = (
            self.env["product.template"]
            .search([("membership_category_id", "in", categories.ids)])
            .filtered(
                lambda t: t.company_id
                and t.company_id != t.membership_category_id.company_id
            )
        )
        if templates:
            raise ValidationError(
                _(
                    "You cannot change the Company, as this "
                    "Membership Category is used by Product Template (%s), "
                    "which has an incompatible assigned Company."
                )
                % fields.first(templates).name
            )
