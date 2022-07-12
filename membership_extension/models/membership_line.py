# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"
    _order = "date_to desc, id desc"

    category_id = fields.Many2one(
        comodel_name="membership.membership_category",
        related="membership_id.membership_category_id",
    )
    date_from = fields.Date(readonly=False)
    date_to = fields.Date(readonly=False)
    state = fields.Selection(
        compute="_compute_state", inverse="_inverse_state", store=True, readonly=False
    )
    partner = fields.Many2one(ondelete="restrict")
    member_price = fields.Float(
        compute="_compute_member_price", readonly=False, store=True
    )

    @api.depends("membership_id")
    def _compute_member_price(self):
        for partner in self:
            partner.member_price = partner.membership_id.list_price

    @api.onchange("date", "membership_id")
    def _onchange_membership_date(self):
        if self.date and self.membership_id:
            self.date_from = self.date
            next_date = self.membership_id._get_next_date(self.date)
            if next_date:
                date_to = next_date - timedelta(1)
                if date_to >= self.date:
                    self.date_to = date_to

    def _compute_state(self):
        # pylint: disable=missing-return
        for line in self:
            if isinstance(line.id, models.NewId) or not line.account_invoice_id:
                line.state = line.state or "none"
            elif (
                line.account_invoice_id.state == "posted"
                and line.account_invoice_id.payment_state == "reversed"
            ):
                line.state = "canceled"
            else:
                return super(MembershipLine, line)._compute_state()

    # Empty method _inverse_state
    def _inverse_state(self):
        return True  # pragma: no cover

    def unlink(self):
        allow = self.env.context.get("allow_membership_line_unlink", False)
        if self.filtered("account_invoice_id") and not allow:
            raise UserError(
                _(
                    "Can not remove membership line related to an "
                    "invoice. Please, cancel invoice or remove invoice "
                    "line instead"
                )
            )
        return super().unlink()  # pragma: no cover
