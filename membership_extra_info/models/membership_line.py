# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    date_decline = fields.Date(
        string="Decline date", readonly=True,
        help="Date when member requested membership withdrawl")
    decline_reason = fields.Many2one(
        string="Decline reason", comodel_name='membership.decline_reason',
        readonly=True)
    category = fields.Many2one(
        string="Category", comodel_name='membership.membership_category',
        related="membership_id.membership_category", readonly=True)
    show_decline_button = fields.Boolean(
        string="Show decline button", readonly=True,
        compute="_compute_show_decline_button")

    @api.depends('date_to', 'date_from', 'date_cancel', 'date_decline',
                 'state')
    def _compute_show_decline_button(self):
        today = fields.Date.today()
        for line in self:
            line.show_decline_button = (
                line.state == 'paid' and
                line.date_from <= today and line.date_to > today and
                not line.date_cancel and not line.date_decline)
        return True

    @api.multi
    def button_decline(self):
        self.ensure_one()
        wizard_form = self.env.ref('membership_extra_info.'
                                   'decline_reason_wizard_form')
        ctx = dict(
            default_membership_line_id=self.id,
            default_date_decline=fields.Date.today(),
            default_date_to=fields.Date.today(),
        )
        return {
            'name': _('Decline membership'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'membership.decline_reason_wizard',
            'views': [(wizard_form.id, 'form')],
            'view_id': wizard_form.id,
            'target': 'new',
            'context': ctx,
        }
