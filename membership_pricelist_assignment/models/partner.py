# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr/).
# @author Damien Horvat <ultrarushgame@gmail.com>
# @author Romain Duciel <romain@mokatourisme.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerInherit(models.Model):
    """Extend the res.partner model.
    Added a existing_pricelist_id field to store the associated pricelist.
    Added a membership_state field to store the membership state of the partner.
    """

    _inherit = "res.partner"

    # Create a new field to store the default pricelist of the partner
    existing_pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Associated Pricelist",
        help="Pricelist to add to the member",
        store=True,
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
        "member_lines.state",
    )
    def _compute_membership_state(self):
        """Compute the membership state of the partner."""
        # Today's date
        today = fields.Date.today()

        for partner in self:
            state = "none"
            # Fetch membership start date
            partner.membership_start = (
                self.env["membership.membership_line"]
                .search(
                    [
                        ("partner", "=", partner.associate_member.id or partner.id),
                        ("date_cancel", "=", False),
                    ],
                    limit=1,
                    order="date_from",
                )
                .date_from
            )
            # Fetch membership end date
            partner.membership_stop = (
                self.env["membership.membership_line"]
                .search(
                    [
                        ("partner", "=", partner.associate_member.id or partner.id),
                        ("date_cancel", "=", False),
                    ],
                    limit=1,
                    order="date_to desc",
                )
                .date_to
            )
            # Fetch membership cancel date
            partner.membership_cancel = (
                self.env["membership.membership_line"]
                .search([("partner", "=", partner.id)], limit=1, order="date_cancel")
                .date_cancel
            )

            if partner.membership_cancel and today > partner.membership_cancel:
                partner.membership_state = "free" if partner.free_member else "canceled"
                continue

            if partner.membership_stop and today > partner.membership_stop:
                if partner.free_member:
                    partner.membership_state = "free"
                else:
                    partner.membership_state = "old"
                continue

            if partner.associate_member:
                partner.membership_state = partner.associate_member.membership_state
                continue

            line_states = [mline.state for mline in partner.member_lines]
            if "paid" in line_states:
                state = "paid"
            elif "invoiced" in line_states:
                state = "invoiced"
            elif "waiting" in line_states:
                state = "waiting"
            elif "canceled" in line_states:
                state = "canceled"
            elif "old" in line_states:
                state = "old"
            if partner.free_member and state != "paid":
                state = "free"
            partner.membership_state = state
