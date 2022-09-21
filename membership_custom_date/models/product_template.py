# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_type = fields.Selection(
        selection_add=[
            ("custom", "Custom dates"),
        ],
        ondelete={"custom": "set default"},
    )

    @api.model
    def _correct_vals_membership_type(self, vals):
        vals = super()._correct_vals_membership_type(vals)
        if vals.get("membership_type") == "custom":
            vals["membership_date_from"] = vals["membership_date_to"] = False
        return vals
