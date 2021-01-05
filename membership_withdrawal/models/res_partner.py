# Copyright 2016 Tecnativa  - Antonio Espinosa
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_last_withdrawal_reason_id = fields.Many2one(
        string="Membership withdrawal reason",
        store=True,
        comodel_name="membership.withdrawal_reason",
        index=True,
        compute="_compute_last_withdrawal",
        help="Withdrawal reason of current membership period",
    )

    membership_last_withdrawal_date = fields.Date(
        string="Membership withdrawal date",
        store=True,
        compute="_compute_last_withdrawal",
        help="Withdrawal date of current membership period",
    )

    @api.depends(
        "membership_state",
        "member_lines.withdrawal_reason_id",
        "member_lines.date_withdrawal",
        "associate_member.membership_last_withdrawal_reason_id",
        "associate_member.membership_last_withdrawal_date",
    )
    def _compute_last_withdrawal(self):
        for partner in self:
            parent = partner.associate_member
            if parent:
                partner.membership_last_withdrawal_reason_id = (
                    parent.membership_last_withdrawal_reason_id
                )
                partner.membership_last_withdrawal_date = (
                    parent.membership_last_withdrawal_date
                )
            else:
                lines = partner.member_lines.filtered(
                    lambda l: l.withdrawal_reason_id and l.date_withdrawal
                ).sorted("date_withdrawal", reverse=True)
                line = fields.first(lines)
                partner.membership_last_withdrawal_reason_id = line.withdrawal_reason_id
                partner.membership_last_withdrawal_date = line.date_withdrawal
