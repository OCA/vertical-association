# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    delegated_member_id = fields.Many2one(
        comodel_name='res.partner',
        string='Delegated Member',
    )

    def _prepare_invoice(self):
        res = super(AccountAnalyticAccount, self)._prepare_invoice()
        res['delegated_member_id'] = self.delegated_member_id.id
        return res
