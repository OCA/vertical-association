# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"
    _order = 'date_to desc, id desc'

    category_id = fields.Many2one(
        string="Category", comodel_name='membership.membership_category',
        related="membership_id.membership_category_id", readonly=True)
    date_from = fields.Date(readonly=False)
    date_to = fields.Date(readonly=False)
    state = fields.Selection(compute=False, inverse=False)
    partner = fields.Many2one(
        ondelete='restrict',
    )

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

    # Two empty methods _compute_state and _inverse_state in order
    # to make state field a regular field (non computed).
    @api.multi
    def _compute_state(self):
        return True  # pragma: no cover

    @api.multi
    def _inverse_state(self):
        return True  # pragma: no cover

    @api.multi
    def unlink(self):
        allow = self.env.context.get('allow_membership_line_unlink', False)
        if self.filtered('account_invoice_id') and not allow:
            raise UserError(
                _('Can not remove membership line related to an '
                  'invoice. Please, cancel invoice or remove invoice '
                  'line instead'))
        return super(MembershipLine, self).unlink()  # pragma: no cover
