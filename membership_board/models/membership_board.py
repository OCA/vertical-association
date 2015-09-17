# -*- coding: utf-8 -*-
# (c) 2015 Incaser Informatica S.L. - Sergio Teruel
# (c) 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class MembershipBoard(models.Model):
    _name = 'membership.board'

    @api.one
    def _compute_president(self):
        position_president_id = self.env.ref(
            'membership_board.'
            'membership_board_position_president')
        member_obj = self.env['membership.board.member']
        president = member_obj.search(
            [('board_id', '=', self.id),
             ('position_id', '=', position_president_id.id),
             ('date_end', '=', False)], limit=1)
        self.president_id = president.partner_id.id

    @api.one
    def _compute_secretary(self):
        position_secretary_id = self.env.ref(
            'membership_board.'
            'membership_board_position_secretary')
        member_obj = self.env['membership.board.member']
        secretary = member_obj.search(
            [('board_id', '=', self.id),
             ('position_id', '=', position_secretary_id.id),
             ('date_end', '=', False)], limit=1)
        self.secretary_id = secretary.partner_id.id

    name = fields.Char('Membership Board', required=True)
    date_start = fields.Date('Init Date')
    date_end = fields.Date('Finish Date')
    note = fields.Text('Description')
    members_ids = fields.One2many(
        comodel_name='membership.board.member',
        inverse_name='board_id', string='Members', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'res.partner'))
    president_id = fields.Many2one(
        compute='_compute_president', comodel_name='res.partner',
        string='President')
    secretary_id = fields.Many2one(
        compute='_compute_secretary', comodel_name='res.partner',
        string='Secretary')

    @api.model
    def delete_all_tags(self, category):
        partner_obj = self.env['res.partner']
        partners = partner_obj.search(
            [('category_id', 'in', category.ids)])
        partners.write({'category_id': [(3, category.id)]})

    @api.multi
    def update_board_tag(self):
        if self.company_id.membership_board_id.id == self.id:
            category = self.env.ref(
                'membership_board.membership_board_tag')
            self.delete_all_tags(category)
            partner_obj = self.env['res.partner']
            partner_ids = []
            for member in self.members_ids.filtered(lambda r: not r.date_end):
                partner_ids.append(member.partner_id.id)
            new_partners = partner_obj.search([('id', 'in', partner_ids)])
            new_partners.write({'category_id': [(4, category.id)]})
        return True

    @api.one
    def write(self, vals):
        res = super(MembershipBoard, self).write(vals)
        if 'members_ids' in vals:
            self.update_board_tag()
        return res


class MembershipBoardPosition(models.Model):
    _name = 'membership.board.position'
    _order = 'name'
    name = fields.Char('Board Position', required=True)


class MembershipBoardMember(models.Model):
    _name = 'membership.board.member'
    _rec_name = 'partner_id'
    _order = 'sequence'

    board_id = fields.Many2one(
        'membership.board', 'Membership Board',
        required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence')
    position_id = fields.Many2one(
        'membership.board.position', 'Position', required=True,
        ondelete='restrict')
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Member', ondelete='restrict')
    note = fields.Text('Note')
    email = fields.Char()
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
