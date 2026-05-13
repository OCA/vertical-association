# Copyright 2026-Today OCA France - Sylvain LE GAL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.misc import str2bool


class MembershipMembershipLine(models.Model):
    _inherit = "membership.membership_line"

    def search(self, domain, offset=0, limit=None, order=None):
        ICP = self.env["ir.config_parameter"].sudo()
        display_waiting = str2bool(
            ICP.get_param(
                "website_membership_non_paid_member.website_display_waiting_membership"
            ),
            default=False,
        )
        display_invoiced = str2bool(
            ICP.get_param(
                "website_membership_non_paid_member.website_display_invoiced_membership"
            ),
            default=False,
        )

        if self.env.context.get("include_not_paid_member") and (
            display_waiting or display_invoiced
        ):
            new_domain = []
            allowed_states = ["paid"]
            if display_waiting:
                allowed_states.append("waiting")
            if display_invoiced:
                allowed_states.append("invoiced")
            for domain_part in domain:
                if domain_part == ("state", "=", "paid"):
                    domain_part = ("state", "in", allowed_states)
                new_domain.append(domain_part)
            return super().search(new_domain, offset=offset, limit=limit, order=order)
        return super().search(domain, offset=offset, limit=limit, order=order)
