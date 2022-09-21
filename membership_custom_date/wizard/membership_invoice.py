# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class MembershipInvoice(models.TransientModel):
    _inherit = "membership.invoice"

    date_from = fields.Date(string="Start Date", default=fields.Datetime.now)
    date_to = fields.Date(string="End Date")

    product_id_type = fields.Selection(
        string="Membership Type",
        related="product_id.membership_type",
    )

    def membership_invoice(self):
        res = super().membership_invoice()

        account_moves = self.env["account.move"].search(res["domain"])
        membership_lines = account_moves.mapped(
            "invoice_line_ids.membership_lines"
        ).filtered(lambda line: line.membership_id.membership_type == "custom")

        membership_lines.write(
            {
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )

        return res
