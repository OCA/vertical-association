# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    membership_state = fields.Selection(
        related="partner_id.membership_state",
        readonly=True,
    )
    membership_start = fields.Date(
        related="partner_id.membership_start",
        readonly=True,
    )
    membership_stop = fields.Date(
        related="partner_id.membership_stop",
        readonly=True,
    )
