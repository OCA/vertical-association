# Copyright 2016 Tecnativa  - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_last_withdrawal_reason_id = fields.Many2one(
        string="Membership withdrawal reason", store=True,
        comodel_name='membership.withdrawal_reason', index=True,
        compute="_compute_last_withdrawal",
        help="Withdrawal reason of current membership period")

    membership_last_withdrawal_date = fields.Date(
        string="Membership withdrawal date", store=True,
        compute="_compute_last_withdrawal",
        help="Withdrawal date of current membership period")

    @api.depends('membership_state', 'member_lines.withdrawal_reason_id',
                 'member_lines.date_withdrawal',
                 'associate_member.membership_last_withdrawal_reason_id',
                 'associate_member.membership_last_withdrawal_date')
    def _compute_last_withdrawal(self):
        for partner in self:
            parent = partner.associate_member
            if parent:
                partner.membership_last_withdrawal_reason_id = \
                    parent.membership_last_withdrawal_reason_id
                partner.membership_last_withdrawal_date = \
                    parent.membership_last_withdrawal_date
            else:
                withdrawal_reason_id = False
                date_withdrawal = False
                for line in partner.member_lines:
                    if line.withdrawal_reason_id and line.date_withdrawal:
                        withdrawal_reason_id = line.withdrawal_reason_id
                        date_withdrawal = line.date_withdrawal
                        break
                partner.membership_last_withdrawal_reason_id = \
                    withdrawal_reason_id.id if withdrawal_reason_id else False
                partner.membership_last_withdrawal_date = date_withdrawal
        return True
