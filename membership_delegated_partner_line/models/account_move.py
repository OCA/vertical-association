# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    is_membership_invoice = fields.Boolean(compute="_compute_is_membership_invoice")

    @api.depends("invoice_line_ids", "line_ids", "move_type")
    @api.onchange("invoice_line_ids", "line_ids", "move_type", "line_ids.product_id")
    def _compute_is_membership_invoice(self):
        for rec in self:
            is_membership_invoice = False
            for line in rec.line_ids:
                if line.product_id.membership:
                    is_membership_invoice = True
                    break
            rec.is_membership_invoice = is_membership_invoice
