# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
try:
    from odoo.addons.membership.models.membership import STATE
except ImportError:
    _logger.warning("Cannot import 'membership' addon.")
    _logger.debug("Details", exc_info=True)

# Max number of days between date_from and date_to of two consecutive
# membership lines to consider a different membership period
LAST_START_DELTA_DAYS = 3


class ResPartner(models.Model):
    _inherit = "res.partner"

    associate_member = fields.Many2one(index=True)
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
        default=fields.Date.today(),
    )
    membership_start = fields.Date(
        string="Membership Start Date",
        readonly=True,
        store=True,
        compute="_compute_membership_date",
        help="Date from which membership becomes active.",
        recursive=True,
    )
    membership_last_start = fields.Date(
        string="Membership Last Start Date",
        readonly=True,
        store=True,
        compute="_compute_membership_date",
        help="Start date of last membership period.",
        recursive=True,
    )
    membership_stop = fields.Date(
        string="Membership End Date",
        readonly=True,
        store=True,
        compute="_compute_membership_date",
        help="Date until which membership remains active.",
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
    membership_category_ids = fields.Many2many(
        string="Membership Categories",
        readonly=True,
        store=True,
        comodel_name="membership.membership_category",
        compute="_compute_membership_state",
        recursive=True,
    )
    membership_categories = fields.Char(
        readonly=True,
        store=True,
        index=True,
        compute="_compute_membership_state",
    )
    membership_state = fields.Selection(
        selection=STATE,
        store=True,
        index=True,
        compute="_compute_membership_state",
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
        return ("invoiced", "paid")

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

    @api.depends(
        "membership_state",
        "is_adhered_member",
        "membership_start_adhered",
        "member_lines.state",
        "member_lines.date_from",
        "member_lines.date_to",
        "member_lines.date_cancel",
        "associate_member.membership_start",
        "associate_member.membership_last_start",
        "associate_member.membership_stop",
        "associate_member.membership_cancel",
    )
    def _compute_membership_date(self):
        member_states = self._membership_member_states()
        for partner in self:
            parent = partner.associate_member
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
                for line in partner.member_lines:
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
                            last_from <= date_to and last_from < line.date_from
                        ):
                            last_from = line.date_from
                        if not last_to or last_to < line_date_to:
                            last_to = line_date_to
                    if not last_cancel or (
                        line.date_cancel and last_cancel < line.date_cancel
                    ):
                        last_cancel = line.date_cancel
                partner.membership_start = date_from
                partner.membership_last_start = last_from
                partner.membership_stop = last_to
                partner.membership_cancel = last_cancel

    @api.depends(
        "free_member",
        "member_lines.state",
        "member_lines.category_id",
        "member_lines.date_from",
        "member_lines.date_to",
        "member_lines.date_cancel",
        "associate_member.membership_state",
        "associate_member.membership_category_ids",
    )
    def _compute_membership_state(self):
        prior = self._membership_state_prior()
        member_states = self._membership_member_states()
        for partner in self:
            if partner.associate_member:
                partner.membership_state = partner.associate_member.membership_state
                partner.membership_category_ids = [
                    (6, False, partner.associate_member.membership_category_ids.ids)
                ]
                partner.membership_categories = (
                    partner.associate_member.membership_categories
                )
            elif partner.free_member:
                partner.membership_state = "free"
                partner.membership_category_ids = [(5, False, False)]
                partner.membership_categories = False
            else:
                state = "none"
                category_ids = []
                category_names = []
                today = fields.Date.today()
                lines = partner.member_lines.filtered(
                    lambda r: r.date_from
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
                if state == "none" and partner.member_lines.filtered(
                    lambda r: r.state in member_states
                ):
                    state = "old"
                partner.membership_state = state
                if category_ids:
                    category_ids = list(set(category_ids))
                    category_names = list(set(category_names))
                    partner.membership_category_ids = [(6, False, category_ids)]
                    partner.membership_categories = ", ".join(category_names)
                else:
                    partner.membership_category_ids = [(5, False, False)]
                    partner.membership_categories = False

    @api.model
    def check_membership_expiry(self):
        """Force a recalculation on expired members"""
        today = fields.Date.today()
        member_states = self._membership_member_states()
        partners = self.search(
            [
                ("associate_member", "=", False),
                ("membership_state", "in", member_states),
                ("membership_stop", "<", today),
            ]
        )
        partners._compute_membership_state()

    @api.model
    def check_membership_all(self):
        """Force a recalculation on partners with member lines"""
        partners = self.search(
            [
                ("associate_member", "=", False),
                ("free_member", "=", False),
                ("member_lines", "!=", False),
            ]
        )
        partners._compute_membership_state()

    @api.model
    def _cron_update_membership(self):
        return self.check_membership_expiry()

    @api.depends("associate_member")
    def _compute_is_adhered_member(self):
        """Prevents is_adhered_member to stay set when no associated member"""
        for partner in self:
            if not partner.associate_member:
                partner.is_adhered_member = False
