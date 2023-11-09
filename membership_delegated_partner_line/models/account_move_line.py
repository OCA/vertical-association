# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    delegated_member_id = fields.Many2one(comodel_name="res.partner")
    is_membership = fields.Boolean(related="product_id.membership")

    def _get_partner_for_membership(self):
        """Auxiliary method for getting the correct membership partner for
        certain operations like initial fee check.
        """
        self.ensure_one()
        return self.delegated_member_id or self.move_id.partner_id

    @api.onchange("product_id")
    def _onchange_product_id_membership(self):
        """If the product is not a membership then we need to set the delegated
        member to False.
        """
        if not self.product_id.membership:
            self.delegated_member_id = False

    @api.onchange("delegated_member_id")
    def _onchange_delegated_member_id(self):
        """If the delegated member is changed then we need to set the description."""
        self.name = self._get_computed_name()

    def _get_computed_name(self):
        name = super()._get_computed_name()
        if self.delegated_member_id:
            name += " (%s)" % self.delegated_member_id.name
        return name
