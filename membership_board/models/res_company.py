# -*- coding: utf-8 -*-
# (c) 2015 Incaser Informatica S.L. - Sergio Teruel
# (c) 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    membership_board_id = fields.Many2one(
        'membership.board', 'Membership Board', ondelete='restrict')

    @api.one
    def write(self, vals):
        result = super(ResCompany, self).write(vals)
        if vals.get('membership_board_id', False):
            self.membership_board_id.update_board_tag()
        else:
            category = self.env.ref(
                'membership_board.membership_board_tag')
            self.membership_board_id.delete_all_tags(category)
        return result
