# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    partner = fields.Many2one(compute="_compute_partner", store=True, readonly=False)

    @api.depends(
        "account_invoice_line.move_id.delegated_member_id",
        "account_invoice_line.move_id.partner_id",
    )
    def _compute_partner(self):
        """Change associated membership lines if delegated member is changed."""
        for membership in self:
            inv_line = membership.account_invoice_line
            if inv_line:
                membership.partner = inv_line._get_partner_for_membership()

    @api.model_create_multi
    def create(self, vals_list):
        """Delegate the member line to the designated partner"""
        for vals in vals_list:
            if "account_invoice_line" not in vals:
                continue
            line = self.env["account.move.line"].browse(vals["account_invoice_line"])
            if line.move_id.delegated_member_id:
                vals["partner"] = line.move_id.delegated_member_id.id
        return super().create(vals_list)

    def write(self, vals):
        """If a partner is delegated, avoid reassign"""
        if "partner" not in vals:
            return super().write(vals)
        if vals.get("account_invoice_line"):
            inv_line = self.env["account.move.line"].browse(
                vals["account_invoice_line"]
            )
        else:
            inv_line = self.account_invoice_line
        if inv_line and inv_line.move_id.delegated_member_id:
            vals["partner"] = inv_line.move_id.delegated_member_id.id
        return super().write(vals)
