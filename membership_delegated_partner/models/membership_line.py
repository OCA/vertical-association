# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    partner_id = fields.Many2one(
        compute="_compute_partner_id", store=True, readonly=False
    )

    @api.depends(
        "account_invoice_line_id.move_id.delegated_member_id",
        "account_invoice_line_id.move_id.partner_id",
    )
    def _compute_partner_id(self):
        """Change associated membership lines if delegated member is changed."""
        for membership in self.filtered(lambda x: x.account_invoice_line_id):
            invoice = membership.account_invoice_line_id.move_id
            if invoice:
                membership.partner_id = (
                    invoice.delegated_member_id or invoice.partner_id
                )

    @api.model_create_multi
    def create(self, vals_list):
        """Delegate the member line to the designated partner"""
        for vals in vals_list:
            if "account_invoice_line_id" not in vals:
                continue
            line = self.env["account.move.line"].browse(vals["account_invoice_line_id"])
            if line.move_id.delegated_member_id:
                vals["partner_id"] = line.move_id.delegated_member_id.id
        return super().create(vals_list)

    def write(self, vals):
        """If a partner is delegated, avoid reassign"""
        if "partner_id" not in vals:
            return super().write(vals)
        if vals.get("account_invoice_line_id"):
            inv_line = self.env["account.move.line"].browse(
                vals["account_invoice_line_id"]
            )
        else:
            inv_line = self.account_invoice_line_id
        if inv_line and inv_line.move_id.delegated_member_id:
            vals["partner_id"] = inv_line.move_id.delegated_member_id.id
        return super().write(vals)
