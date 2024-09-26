# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    partner = fields.Many2one(compute="_compute_partner", store=True, readonly=False)

    @api.depends(
        "account_invoice_line.delegated_member_id",
        "account_invoice_line.move_id.partner_id",
    )
    def _compute_partner(self):
        """Change associated membership lines if delegated member is changed.
        NOTE: This is required due to the weird way that account.move in parent
        membership module writes the membership partner.
        """
        for membership in self:
            inv_line = membership.account_invoice_line
            if inv_line:
                membership.partner = inv_line._get_partner_for_membership()

    @api.model
    def create(self, vals):
        """Delegate the member line to the designated partner"""
        if "account_invoice_line" not in vals:
            return super().create(vals)
        line = self.env["account.move.line"].browse(vals["account_invoice_line"])
        if line.delegated_member_id:
            vals["partner"] = line.delegated_member_id.id
        return super().create(vals)

    def write(self, vals):
        """If a partner is delegated, avoid reassign"""
        if "partner" not in vals:
            return super().write(vals)
        if vals.get("account_invoice_line"):
            inv_line = self.env["account.move.line"].browse(
                vals["account_invoice_line"]
            )
            if inv_line and inv_line.delegated_member_id:
                vals["partner"] = inv_line.delegated_member_id.id
        else:
            for record in self:
                record.partner = (
                    record.account_invoice_line._get_partner_for_membership()
                )
        return super().write(vals)
