# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_draft(self):
        # OVERRIDE to update the cancel date.
        res = super().button_draft()
        for move in self.filtered(lambda x: x.move_type == "out_invoice"):
            lines = move.invoice_line_ids.membership_line_ids
            if lines:
                lines.write({"date_cancel": False})
        return res

    def button_cancel(self):
        # OVERRIDE to update the cancel date.
        res = super().button_cancel()
        for move in self.filtered(lambda x: x.move_type == "out_invoice"):
            lines = move.invoice_line_ids.membership_line_ids
            if lines:
                lines.write({"date_cancel": fields.Date.context_today(self)})
        return res

    def write(self, vals):
        # OVERRIDE to write the partner on the membership lines.
        res = super().write(vals)
        if "partner_id" in vals:
            lines = self.invoice_line_ids.membership_line_ids
            if lines:
                lines.write({"partner_id": vals["partner_id"]})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    membership_line_ids = fields.One2many(
        "membership.membership_line",
        "account_invoice_line_id",
        string="Membership lines",
    )

    def _prepare_membership_line_vals(self, **kwargs):
        self.ensure_one()
        return {
            "partner_id": self.move_id.partner_id.id,
            "membership_id": self.product_id.id,
            "member_price": self.price_unit,
            "date": fields.Date.context_today(self),
            "date_from": kwargs.get("date_from"),
            "date_to": kwargs.get("date_to"),
            "account_invoice_line_id": self.id,
        }

    def _create_membership_line(self):
        to_process = self.filtered(
            lambda line: line.move_id.move_type == "out_invoice"
            and line.product_id.membership
        )
        # Nothing to process, break.
        if not to_process:
            return
        existing_memberships = to_process.membership_line_ids
        to_process = to_process - existing_memberships.mapped("account_invoice_line_id")
        # All memberships already exist, break.
        if not to_process:
            return
        memberships_vals = []
        for line in to_process:
            date_from = line.product_id.membership_date_from
            date_to = line.product_id.membership_date_to
            if date_from and date_from < (line.move_id.invoice_date or date.min) < (
                date_to or date.min
            ):
                date_from = line.move_id.invoice_date
            memberships_vals.append(
                line._prepare_membership_line_vals(date_from=date_from, date_to=date_to)
            )
        self.env["membership.membership_line"].create(memberships_vals)

    def write(self, vals):
        res = super().write(vals)
        self._create_membership_line()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._create_membership_line()
        return lines
