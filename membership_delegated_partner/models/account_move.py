# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    delegated_member_id = fields.Many2one(comodel_name="res.partner")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_partner_for_membership(self):
        """Auxiliary method for getting the correct membership partner for
        certain operations like initial fee check.
        """
        self.ensure_one()
        return self.move_id.delegated_member_id or self.move_id.partner_id
