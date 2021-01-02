# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_default_journal(self):
        if not self._context.get("default_membership_receipt", False):
            # If not a membership receipt, do nothing
            return super(AccountMove, self)._get_default_journal()
        return self.env["account.journal"].get_membership_receipt_journal()

    journal_id = fields.Many2one(default=_get_default_journal)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)

        to_process = self.filtered(
            lambda line: line.move_id.move_type == "out_receipt"
            and line.product_id.membership
        )

        # Nothing to process, break.
        if not to_process:
            return res

        existing_memberships = self.env["membership.membership_line"].search(
            [("account_invoice_line", "in", to_process.ids)]
        )
        to_process = to_process - existing_memberships.mapped("account_invoice_line")

        # All memberships already exist, break.
        if not to_process:
            return res

        memberships_vals = []
        for line in to_process:
            date_from = line.product_id.membership_date_from
            date_to = line.product_id.membership_date_to
            if date_from and date_from < (line.move_id.invoice_date or date.min) < (
                date_to or date.min
            ):
                date_from = line.move_id.invoice_date
            memberships_vals.append(
                {
                    "partner": line.move_id.partner_id.id,
                    "membership_id": line.product_id.id,
                    "member_price": line.price_unit,
                    "date": fields.Date.today(),
                    "date_from": date_from,
                    "date_to": date_to,
                    "account_invoice_line": line.id,
                }
            )
        self.env["membership.membership_line"].create(memberships_vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(AccountMoveLine, self).create(vals_list)
        to_process = lines.filtered(
            lambda line: line.move_id.move_type == "out_receipt"
            and line.product_id.membership
        )

        # Nothing to process, break.
        if not to_process:
            return lines

        existing_memberships = self.env["membership.membership_line"].search(
            [("account_invoice_line", "in", to_process.ids)]
        )
        to_process = to_process - existing_memberships.mapped("account_invoice_line")

        # All memberships already exist, break.
        if not to_process:
            return lines

        memberships_vals = []
        for line in to_process:
            date_from = line.product_id.membership_date_from
            date_to = line.product_id.membership_date_to
            if date_from and date_from < (line.move_id.invoice_date or date.min) < (
                date_to or date.min
            ):
                date_from = line.move_id.invoice_date
            memberships_vals.append(
                {
                    "partner": line.move_id.partner_id.id,
                    "membership_id": line.product_id.id,
                    "member_price": line.price_unit,
                    "date": fields.Date.today(),
                    "date_from": date_from,
                    "date_to": date_to,
                    "account_invoice_line": line.id,
                }
            )
        self.env["membership.membership_line"].create(memberships_vals)
        return lines
