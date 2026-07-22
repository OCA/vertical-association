# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import Command, api, fields, models
from odoo.exceptions import UserError, ValidationError

# Max number of days between date_from and date_to of two consecutive
# membership lines to consider a different membership period
LAST_START_DELTA_DAYS = 3


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_adhered_member = fields.Boolean(
        compute="_compute_is_adhered_member",
        store=True,
        readonly=False,
        help="A member who is associated to another one, but whose membership "
        "are independent.",
    )
    membership_start_adhered = fields.Date(
        string="Membership Adhered Start Date",
        help="Date from which partner is adhered.",
        default=lambda self: fields.Date.context_today(self),
    )
    membership_category_ids = fields.Many2many(
        string="Membership Categories",
        readonly=True,
        store=True,
        comodel_name="membership.membership_category",
        compute="_compute_membership_state",
        recursive=True,
    )
    associate_member_id = fields.Many2one(
        "res.partner",
        index=True,
        help="A member with whom you want to associate your membership."
        "It will consider the membership state of the associated member.",
    )
    member_line_ids = fields.One2many(
        "membership.membership_line", "partner_id", string="Membership"
    )
    free_member = fields.Boolean(help="Select if you want to give free membership.")
    membership_amount = fields.Float(
        digits=(16, 2),
        help="The price negotiated by the partner",
    )
    membership_state = fields.Selection(
        selection=lambda self: self.env["membership.membership_line"]
        ._fields["state"]
        .selection,
        compute="_compute_membership_state",
        string="Current Membership Status",
        store=True,
        recursive=True,
        index=True,
        help="It indicates the membership state.\n"
        "-Non Member: A partner who has not applied for any membership.\n"
        "-Cancelled Member: A member who has cancelled his membership.\n"
        "-Old Member: A member whose membership date has expired.\n"
        "-Waiting Member: A member who has applied for the membership and whose "
        "invoice is going to be created.\n"
        "-Invoiced Member: A member whose invoice has been created.\n"
        "-Paying member: A member who has paid the membership fee.",
    )
    membership_start = fields.Date(
        string="Membership Start Date",
        readonly=True,
        store=True,
        compute="_compute_membership_date",
        help="Earliest historical date this partner ever became a member.",
        recursive=True,
    )
    membership_last_start = fields.Date(
        string="Membership Last Start Date",
        readonly=True,
        store=True,
        compute="_compute_membership_date",
        help="Date when the partner became a member for the last time.",
        recursive=True,
    )
    membership_stop = fields.Date(
        string="Membership End Date",
        readonly=True,
        store=True,
        compute="_compute_membership_date",
        help="Date when the latest partner's membership ends.",
        recursive=True,
    )
    membership_cancel = fields.Date(
        string="Cancel Membership Date",
        readonly=True,
        store=True,
        compute="_compute_membership_date",
        help="Date on which membership has been cancelled.",
        recursive=True,
    )

    @api.model
    def _last_start_delta_days(self):
        """Inherit this method to change last_start_delta_days param

        Max allowed days between membership periods in order to consider
        a continuos period
        """
        return LAST_START_DELTA_DAYS

    def _membership_member_states(self):
        """Inherit this method to define membership states

        List of membership line states that define a partner as member
        """
        return ("invoiced", "free", "paid")

    def _membership_state_prior(self):
        """Inherit this method to define membership state precedence

        Dictionary with precendence of each state
        """
        state_prior = {
            "none": 0,
            "canceled": 1,
            "old": 2,
            "waiting": 3,
            "invoiced": 4,
            "free": 6,
            "paid": 7,
        }
        return state_prior

    @api.depends("associate_member_id")
    def _compute_is_adhered_member(self):
        """Prevents is_adhered_member to stay set when no associated member"""
        for partner in self:
            if not partner.associate_member_id:
                partner.is_adhered_member = False

    @api.depends(
        "membership_state",
        "is_adhered_member",
        "membership_start_adhered",
        "member_line_ids.state",
        "member_line_ids.date_from",
        "member_line_ids.date_to",
        "member_line_ids.date_cancel",
        "associate_member_id.membership_start",
        "associate_member_id.membership_last_start",
        "associate_member_id.membership_stop",
        "associate_member_id.membership_cancel",
    )
    def _compute_membership_date(self):
        member_states = self._membership_member_states()
        for partner in self:
            parent = partner.associate_member_id
            if parent:
                partner.membership_start = (
                    partner.membership_start_adhered
                    if partner.is_adhered_member
                    else parent.membership_start
                )
                partner.membership_last_start = parent.membership_last_start
                partner.membership_stop = parent.membership_stop
                partner.membership_cancel = parent.membership_cancel
            else:
                date_from = False
                last_from = False
                last_to = False
                last_cancel = False
                for line in partner.member_line_ids.sorted():
                    if line.state in member_states:
                        if not date_from or date_from > line.date_from:
                            date_from = line.date_from
                        delta = self._last_start_delta_days()
                        line_date_to = line.date_to
                        if line.date_cancel:
                            line_date_to = line.date_cancel
                        if not line_date_to:
                            continue
                        date_to = line_date_to + timedelta(days=delta)
                        if not last_from or (
                            last_from <= date_to and last_from > line.date_from
                        ):
                            last_from = line.date_from
                        if not last_to or last_to < line_date_to:
                            last_to = line_date_to
                    if not last_cancel or (
                        line.date_cancel and last_cancel < line.date_cancel
                    ):
                        last_cancel = line.date_cancel
                    if last_cancel and last_from and last_cancel < last_from:
                        # Membership was restarted after a cancellation
                        last_cancel = False
                partner.membership_start = date_from
                partner.membership_last_start = last_from
                partner.membership_stop = last_to
                partner.membership_cancel = last_cancel

    @api.depends(
        "member_line_ids.account_invoice_line_id",
        "member_line_ids.account_invoice_line_id.move_id.state",
        "member_line_ids.account_invoice_line_id.move_id.payment_state",
        "member_line_ids.account_invoice_line_id.move_id.partner_id",
        "free_member",
        "member_line_ids.state",
        "member_line_ids.category_id",
        "member_line_ids.date_to",
        "member_line_ids.date_from",
        "member_line_ids.date_cancel",
        "associate_member_id",
        "associate_member_id.membership_state",
        "associate_member_id.membership_category_ids",
    )
    def _compute_membership_state(self):
        today = fields.Date.context_today(self)
        prior = self._membership_state_prior()
        member_states = self._membership_member_states()
        for partner in self:
            if partner.associate_member_id:
                partner.membership_state = partner.associate_member_id.membership_state
                partner.membership_category_ids = [
                    Command.set(partner.associate_member_id.membership_category_ids.ids)
                ]
                continue
            if partner.free_member:
                partner.membership_state = "free"
                partner.membership_category_ids = [Command.clear()]
                continue
            state = "none"
            category_ids = []
            category_names = []
            lines = partner.member_line_ids.filtered(
                lambda r, today=today: r.date_from
                and r.date_from <= today
                and (
                    (r.date_to and r.date_to >= today)
                    and (not r.date_cancel or r.date_cancel >= today)
                )
            )
            # Use default language for getting category names
            for line in lines.with_context(lang="en_US"):
                if line.state in member_states and line.category_id:
                    category_ids.append(line.category_id.id)
                    category_names.append(line.category_id.name)
                if prior.get(line.state, 0) > prior.get(state):
                    state = line.state
            if state == "none" and partner.member_line_ids.filtered(
                lambda r: r.state in member_states
            ):
                state = "old"
            partner.membership_state = state
            if category_ids:
                category_ids = list(set(category_ids))
                category_names = list(set(category_names))
                partner.membership_category_ids = [Command.set(category_ids)]
            else:
                partner.membership_category_ids = [Command.clear()]

    @api.constrains("associate_member_id")
    def _check_recursion_associate_member(self):
        if self._has_cycle("associate_member_id"):
            raise ValidationError(
                self.env._("You cannot create recursive associated members.")
            )

    @api.model
    def _cron_update_membership(self):
        return self.check_membership_expiry()

    @api.model
    def check_membership_expiry(self):
        """Force a recalculation on expired members"""
        today = fields.Date.context_today(self)
        member_states = self._membership_member_states()
        partners = self.search(
            [
                ("associate_member_id", "=", False),
                ("membership_state", "in", member_states),
                ("membership_stop", "<", today),
            ]
        )
        partners._compute_membership_state()

    def create_membership_invoice(self, product, amount):
        """Create Customer Invoice of Membership for partners."""
        invoice_vals_list = []
        for partner in self:
            addr = partner.address_get(["invoice"])
            if partner.free_member:
                raise UserError(self.env._("Partner is a free Member."))
            if not addr.get("invoice", False):
                raise UserError(
                    self.env._("Partner doesn't have an address to make the invoice.")
                )
            invoice_vals_list.append(
                partner._prepare_membership_invoice(product, amount)
            )
        return self.env["account.move"].create(invoice_vals_list)

    def _prepare_membership_invoice(self, product, amount):
        return {
            "move_type": "out_invoice",
            "partner_id": self.id,
            "invoice_line_ids": [
                Command.create(self._prepare_membership_invoice_line(product, amount)),
            ],
        }

    def _prepare_membership_invoice_line(self, product, amount):
        return {
            "product_id": product.id,
            "quantity": 1,
            "price_unit": amount,
            "tax_ids": [
                Command.set(
                    product.taxes_id.filtered_domain(
                        self.env["account.tax"]._check_company_domain(self.env.company)
                    ).ids,
                )
            ],
        }
