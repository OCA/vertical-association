# Copyright 2022 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    membership_id = fields.Many2one(
        "product.product",
        string="Membership",
        store=True,
        compute="_compute_membership_state",
    )

    @api.depends(
        "member_lines.account_invoice_line",
        "member_lines.account_invoice_line.move_id.state",
        "member_lines.account_invoice_line.move_id.payment_state",
        "member_lines.account_invoice_line.move_id.partner_id",
        "free_member",
        "member_lines.date_to",
        "member_lines.date_from",
        "associate_member",
    )
    def _compute_membership_state(self):
        super()._compute_membership_state()
        for partner in self:
            partner.membership_id = (
                self.env["membership.membership_line"]
                .search(
                    [
                        ("partner", "=", partner.associate_member.id or partner.id),
                        ("date_cancel", "=", False),
                    ],
                    limit=1,
                    order="date_to",
                )
                .membership_id
            )
