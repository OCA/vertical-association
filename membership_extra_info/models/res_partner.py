# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from openerp import models, fields, api

# Max number of days between date_from and date_to of two consecutive
# membership lines to consider a different membership period
LAST_START_DELTA_DAYS = 3


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_last_start = fields.Date(
        string="Membership last start date", store=True, readonly=True,
        compute="_compute_last",
        help="Start date of last membership period")

    membership_last_decline_reason = fields.Many2one(
        string="Membership decline reason", store=True, readonly=True,
        comodel_name='membership.decline_reason', compute="_compute_last",
        help="Decline reason of current membership period")

    membership_last_decline_date = fields.Date(
        string="Membership decline date", store=True, readonly=True,
        compute="_compute_last",
        help="Decline date of current membership period")

    membership_last_category = fields.Many2one(
        string="Membership category", store=True, readonly=True,
        comodel_name='membership.membership_category',
        compute="_compute_last",
        help="Membership category of current membership period")

    @api.depends('member_lines.date_from', 'member_lines.state',
                 'member_lines.category', 'member_lines.decline_reason',
                 'member_lines.date_decline', 'associate_member',
                 'associate_member.membership_last_start',
                 'associate_member.membership_last_category',
                 'associate_member.membership_last_decline_reason',
                 'associate_member.membership_last_decline_date')
    def _compute_last(self):
        for partner in self:
            if partner.associate_member:
                partner.membership_last_start = \
                    partner.associate_member.membership_last_start
                partner.membership_last_category = \
                    partner.associate_member.membership_last_category
                partner.membership_last_decline_reason = \
                    partner.associate_member.membership_last_decline_reason
                partner.membership_last_decline_date = \
                    partner.associate_member.membership_last_decline_date
            elif not partner.member_lines:
                partner.membership_last_start = False
                partner.membership_last_category = False
                partner.membership_last_decline_reason = False
                partner.membership_last_decline_date = False
            else:
                last_from = False
                category = False
                decline_reason = False
                date_decline = False
                for line in partner.member_lines:
                    if line.state in ('invoiced', 'paid'):
                        if not category:
                            category = line.category
                        if not decline_reason:
                            decline_reason = line.decline_reason
                        if not date_decline:
                            date_decline = line.date_decline
                        delta = (fields.Date.from_string(line.date_to) +
                                 timedelta(days=LAST_START_DELTA_DAYS))
                        delta_str = fields.Date.to_string(delta)
                        if not last_from or last_from <= delta_str:
                            last_from = line.date_from
                        else:
                            break
                partner.membership_last_start = last_from
                partner.membership_last_category = \
                    category.id if category else False
                partner.membership_last_decline_reason = \
                    decline_reason.id if decline_reason else False
                partner.membership_last_decline_date = date_decline
        return True
