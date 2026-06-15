# Copyright 2026 AKRETION
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    date_from = fields.Date(
        compute="_compute_from_to_dates",
        store=True,
        readonly=False,
    )
    date_to = fields.Date(
        compute="_compute_from_to_dates",
        store=True,
        readonly=False,
    )
    move_state = fields.Selection(
        related="account_invoice_line.parent_state",
    )

    @api.constrains("account_invoice_line")
    def _constrain_multiple_membership_per_invoice_line(self):
        """Prevent N membership lines for 1 account move line,
        to ensure the start & end dates can be synchronized between
        membership line & account move line"""
        lines = self.filtered("account_invoice_line")
        if lines and lines != lines.account_invoice_line.membership_lines:
            raise exceptions.ValidationError(
                _("Only 1 membership is allowed per invoice line.")
            )

    @api.constrains("date_from", "date_to")
    def _constrain_from_to_dates_confirmed_invoices(self):
        """Prevent updating dates on membership lines if the invoice
        is confirmed"""
        if self.filtered(lambda x: x.move_state == "posted"):
            raise exceptions.ValidationError(
                _(
                    "The From and To dates cannot be modified once the invoice "
                    "is confirmed. Please set the invoice back to draft and try "
                    "again."
                )
            )

    @api.depends("account_invoice_line.start_date", "account_invoice_line.end_date")
    def _compute_from_to_dates(self):
        if self._context.get("membership_prevent_recursive_dates"):
            return
        for line in self.with_context(membership_prevent_recursive_dates=True):
            line.write(
                {
                    "date_from": line.account_invoice_line.start_date,
                    "date_to": line.account_invoice_line.end_date,
                }
            )
