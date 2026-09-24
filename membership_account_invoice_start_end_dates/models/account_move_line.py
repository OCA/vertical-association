# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    start_date = fields.Date(
        compute="_compute_start_end_dates",
        store=True,
        readonly=False,
    )
    end_date = fields.Date(
        compute="_compute_start_end_dates",
        store=True,
        readonly=False,
    )

    @api.depends("membership_lines.date_from", "membership_lines.date_to")
    def _compute_start_end_dates(self):
        if self._context.get("membership_prevent_recursive_dates"):
            return
        lines = self.filtered("membership_lines")
        for line in lines.with_context(membership_prevent_recursive_dates=True):
            line.write(
                {
                    "start_date": line.membership_lines.date_from,
                    "end_date": line.membership_lines.date_to,
                }
            )

    def write(self, vals):
        self = self.with_context(skip_constrain_dates_membership=True)
        return super().write(vals)
