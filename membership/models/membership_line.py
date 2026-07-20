# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe

from datetime import timedelta

from odoo import api, fields, models
from odoo.api import NewId
from odoo.exceptions import UserError


class MembershipLine(models.Model):
    _name = "membership.membership_line"
    _rec_name = "partner_id"
    _order = "date_to desc, id desc"
    _description = "Membership Line"

    partner_id = fields.Many2one(
        "res.partner", string="Partner", ondelete="restrict", index=True
    )
    membership_id = fields.Many2one(
        "product.product", string="Membership", required=True
    )
    category_id = fields.Many2one(
        comodel_name="membership.membership_category",
        related="membership_id.membership_category_id",
    )
    date_from = fields.Date(string="From", readonly=False)
    date_to = fields.Date(string="To", readonly=False)
    date_cancel = fields.Date(string="Cancel date")
    date = fields.Date(
        string="Join Date", help="Date on which member has joined the membership"
    )
    member_price = fields.Float(
        string="Membership Fee",
        min_display_digits="Product Price",
        compute="_compute_member_price",
        readonly=False,
        store=True,
        required=True,
        help="Amount for the membership",
    )
    account_invoice_line_id = fields.Many2one(
        "account.move.line",
        string="Account Invoice line",
        readonly=True,
        ondelete="cascade",
    )
    account_invoice_id = fields.Many2one(
        "account.move",
        related="account_invoice_line_id.move_id",
        string="Invoice",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="account_invoice_line_id.move_id.company_id",
        string="Company",
        readonly=True,
        store=True,
    )
    state = fields.Selection(
        selection=[
            ("none", "Non Member"),
            ("canceled", "Cancelled Member"),
            ("old", "Old Member"),
            ("waiting", "Waiting Member"),
            ("invoiced", "Invoiced Member"),
            ("free", "Free Member"),
            ("paid", "Paid Member"),
        ],
        compute="_compute_state",
        string="Membership Status",
        store=True,
        readonly=False,
        help="It indicates the membership status.\n"
        "-Non Member: A member who has not applied for any membership.\n"
        "-Cancelled Member: A member who has cancelled his membership.\n"
        "-Old Member: A member whose membership date has expired.\n"
        "-Waiting Member: A member who has applied for the membership and whose "
        "invoice is going to be created.\n"
        "-Invoiced Member: A member whose invoice has been created.\n"
        "-Paid Member: A member who has paid the membership amount.",
    )

    _start_date_greater = models.Constraint(
        "check(date_to >= date_from)",
        "Error ! Ending Date cannot be set before Beginning Date.",
    )

    @api.depends("membership_id")
    def _compute_member_price(self):
        for partner in self:
            partner.member_price = partner.membership_id.list_price

    @api.depends(
        "account_invoice_id.state",
        "account_invoice_id.amount_residual",
        "account_invoice_id.payment_state",
    )
    def _compute_state(self):
        """Compute the state lines"""
        if not self:
            return
        groups = (
            self.env["account.move"]
            .sudo()
            ._read_group(
                domain=[("reversed_entry_id", "in", self.account_invoice_id.ids)],
                groupby=["reversed_entry_id"],
                aggregates=["__count"],
            )
        )
        reverse_map = {move.id: count for move, count in groups}
        no_invoice_lines = self.filtered(
            lambda line: isinstance(line.id, NewId) or not line.account_invoice_id
        )
        cancelled_lines = self.filtered(
            lambda line: line.account_invoice_id.state == "posted"
            and line.account_invoice_id.payment_state == "reversed"
        )
        cancelled_lines.state = "canceled"
        for line in no_invoice_lines:
            line.state = line.state or "none"
        remaining_lines = self - no_invoice_lines - cancelled_lines
        for line in remaining_lines:
            move_state = line.account_invoice_id.state
            payment_state = line.account_invoice_id.payment_state
            line.state = "none"
            if move_state == "draft":
                line.state = "waiting"
            elif move_state == "posted":
                if payment_state == "paid":
                    if reverse_map.get(line.account_invoice_id.id):
                        line.state = "canceled"
                    else:
                        line.state = "paid"
                elif payment_state == "in_payment":
                    line.state = "paid"
                elif payment_state in ("not_paid", "partial"):
                    line.state = "invoiced"
            elif move_state == "cancel":
                line.state = "canceled"

    @api.onchange("date", "membership_id")
    def _onchange_membership_date(self):
        if self.date and self.membership_id:
            self.date_from = self.date
            next_date = self.membership_id._get_next_date(self.date)
            if next_date:
                date_to = next_date - timedelta(1)
                if date_to >= self.date:
                    self.date_to = date_to

    @api.ondelete(at_uninstall=False)
    def _unlink_membership_line_except_invoiced(self):
        allow = self.env.context.get("allow_membership_line_unlink", False)
        if self.filtered("account_invoice_id") and not allow:
            raise UserError(
                self.env._(
                    "Can not remove membership line related to an "
                    "invoice. Please, cancel invoice or remove invoice "
                    "line instead"
                )
            )
