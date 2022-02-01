# Copyright 2021 Manuel Calero <mcalero@xtendoo.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_birth_date = fields.Date("Birthdate")
    membership_age = fields.Integer(string="Age", readonly=True, compute="_compute_age")
    membership_since_date = fields.Date("Membership since")

    @api.depends("membership_birth_date")
    def _compute_age(self):
        for record in self:
            membership_age = 0
            if record.membership_birth_date:
                membership_age = relativedelta(
                    fields.Date.today(), record.membership_birth_date
                ).years
            record.membership_age = membership_age
