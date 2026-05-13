# Copyright 2026-Today OCA France - Sylvain LE GAL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_display_waiting_membership = fields.Boolean(
        string="Display members if they have a draft membership invoice",
        config_parameter="website_membership_non_paid_member.website_display_waiting_membership",
    )
    website_display_invoiced_membership = fields.Boolean(
        string="Display members if they have a confirmed membership invoice",
        config_parameter="website_membership_non_paid_member.website_display_invoiced_membership",
    )
