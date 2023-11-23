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
    dates_mandatory = fields.Boolean(
        string="Mandatory dates",
        default=True,
        help="Membership lines that use this product must have a start and end date.",
    )

    @api.model
    def _correct_vals_membership_type(self, vals):
        vals = super()._correct_vals_membership_type(vals)
        if vals.get("membership_type") == "custom":
            vals["membership_date_from"] = vals["membership_date_to"] = False
        # TODO: should we set dates_mandatory back to True if switching away
        # from custom? At the moment this variable is not used _at all_ for
        # non-custom memberships.
        return vals
