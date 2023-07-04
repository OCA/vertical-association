# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    is_membership_invoice = fields.Boolean(compute="_compute_is_membership_invoice")

    @api.depends("invoice_line_ids", "line_ids", "move_type")
    @api.onchange("invoice_line_ids", "line_ids", "move_type", "line_ids.product_id")
    def _compute_is_membership_invoice(self):
        for rec in self:
            if rec.move_type.startswith("out_"):
                rec.is_membership_invoice = any(
                    rec.line_ids.mapped("product_id.membership")
                )
            else:
                rec.is_membership_invoice = False
