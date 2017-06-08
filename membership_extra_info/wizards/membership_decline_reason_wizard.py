# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class MembershipDeclineReasonWizard(models.TransientModel):
    _name = "membership.decline_reason_wizard"
    _description = "Decline membership"

    membership_line_id = fields.Many2one(
        comodel_name='membership.membership_line', required=True)
    date_decline = fields.Date(
        string="Decline date", required=True,
        help="Date when member requested membership withdrawl")
    date_to = fields.Date(
        string="New finish date",
        help="New finish date in membership line. Date when user wants that "
             "membership withdrawl really applies")
    decline_reason = fields.Many2one(
        string="Decline reason", comodel_name='membership.decline_reason',
        required=True)

    @api.multi
    def decline(self):
        if not self.membership_line_id:
            raise UserError(_('No membership line selected'))
        state = self.membership_line_id.state
        data = {
            'date_decline': self.date_decline,
            'decline_reason': self.decline_reason.id,
            # Workaround (part 1) in order to update partner.membership_stop
            # to the new date_to
            'state': 'canceled' if state != 'canceled' else 'paid',
        }
        if (self.date_to and
                self.membership_line_id.date_to > self.date_to and
                self.membership_line_id.date_from <= self.date_to):
            data['date_to'] = self.date_to
        self.membership_line_id.write(data)
        # Workaround (part 2) in order to update partner.membership_stop
        # to the new date_to
        self.membership_line_id.write({'state': state})
        return {'type': 'ir.actions.act_window_close'}
