# Copyright 2016 Tecnativa  - Antonio Espinosa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    date_withdrawal = fields.Date(
        string="Withdrawal date",
        help="Date when member requested membership withdrawal",
    )
    withdrawal_reason_id = fields.Many2one(
        string="Withdrawal reason", comodel_name="membership.withdrawal_reason"
    )
