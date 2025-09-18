# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import random

from odoo import models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    def search(self, domain, offset=0, limit=None, order=None):
        """If we detect the injected context, and only when the search is done with
        limit (as there are 2 calls to search in the controller), we search for all
        the results, randomize them, and return them. We can't do slices, as if not, we
        won't be able to show all the records due to the pager and each time returning
        random results.
        """
        if self.env.context.get("random_membership_line_order") and limit:
            record_ids = super().search(domain, limit=None).ids
            random.shuffle(record_ids)
            return self.browse(record_ids)
        return super().search(domain, offset=offset, limit=limit, order=order)
