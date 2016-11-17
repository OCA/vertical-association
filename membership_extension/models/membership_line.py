# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.addons.membership.membership import STATE


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"
    _order = 'date_to desc, id desc'

    category_id = fields.Many2one(
        string="Category", comodel_name='membership.membership_category',
        related="membership_id.membership_category_id", readonly=True)
    date_from = fields.Date(readonly=False)
    date_to = fields.Date(readonly=False)
    state = fields.Selection(
        selection=STATE, readonly=False,
        compute='_compute_state', inverse="_inverse_state",
    )

    def __init__(self, pool, cr):
        super(MembershipLine, self).__init__(pool, cr)
        for model, store in pool._store_function.iteritems():
            pool._store_function[model] = [
                x for x in store
                if x[0] != 'membership.membership_line' and x[1] != 'state']

    @api.onchange('membership_id')
    def _onchange_membership_id(self):
        self.member_price = self.membership_id.list_price
        self._onchange_date()

    @api.onchange('date')
    def _onchange_date(self):
        if self.date and self.membership_id:
            date = fields.Date.from_string(self.date)
            self.date_from = self.date
            next_date = self.membership_id._get_next_date(date)
            if next_date:
                date_to = fields.Date.to_string(next_date - timedelta(1))
                if date_to >= self.date:
                    self.date_to = date_to

    # Define two empty methods _compute_state and _inverse_state in order
    # to make state field a regular field (non computed).
    @api.multi
    def _compute_state(self):
        return True  # pragma: no cover

    @api.multi
    def _inverse_state(self):
        return True  # pragma: no cover

    @api.multi
    def unlink(self):
        model = self.env.context.get('params', {}).get('model', False)
        action_id = self.env.context.get('params', {}).get('action', False)
        active_model = self.env.context.get('active_model', False)
        if not model and action_id:
            action = self.env['ir.actions.act_window'].browse(action_id)
            model = action.res_model
        if not model and active_model:
            model = active_model
        if model == 'res.partner' and self.filtered('account_invoice_id'):
            raise UserError(
                _('Can not remove membership line related to an '
                  'invoice. Please, cancel invoice or remove invoice '
                  'line instead'))
        return super(MembershipLine, self).unlink()
