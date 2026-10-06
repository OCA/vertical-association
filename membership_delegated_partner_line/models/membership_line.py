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

    @api.model_create_multi
    def create(self, vals_list):
        """Delegate the member line to the designated partner when applicable."""
        for vals in vals_list:
            account_line_id = vals.get("account_invoice_line")
            if not account_line_id:
                continue
            line = self.env["account.move.line"].browse(account_line_id)
            delegated_partner = line.delegated_member_id
            if delegated_partner:
                vals["partner"] = delegated_partner.id
        return super().create(vals_list)

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
            return super().write(vals)
        else:
            for record in self:
                partner = (
                    record.account_invoice_line
                    and record.account_invoice_line._get_partner_for_membership()
                    or None
                )
                if partner:
                    vals["partner"] = partner.id
                super(MembershipLine, record).write(vals)
            return True
