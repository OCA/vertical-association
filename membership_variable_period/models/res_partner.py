# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def check_membership_expiry(self):
        """Force a recalculation on each partner that is member."""
        partners = self.search(
            [('membership_state', 'not in', ['old', 'none', 'free']),
             ('associate_member', '=', False)])
        # It has to be triggered one by one to avoid an error
        for partner in partners:
            partner.write({'membership_state': 'none'})
        return True
