# Copyright 2026-Today OCA France - Sylvain LE GAL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request, route
from odoo.tools import frozendict

from odoo.addons.website_membership.controllers.main import WebsiteMembership


class WebsiteMembership(WebsiteMembership):
    @route()
    def members(
        self, membership_id=None, country_name=None, country_id=0, page=1, **post
    ):
        """Inject a context for being queried later on the search
        of the membership lines for including not paid members.
        """

        request.env.context = frozendict(
            request.env.context, include_not_paid_member=True
        )
        return super().members(
            membership_id=membership_id,
            country_name=country_name,
            country_id=country_id,
            page=page,
            **post,
        )
