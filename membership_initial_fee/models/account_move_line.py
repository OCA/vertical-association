# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo import api, models
from odoo.tools.translate import _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_initial_fee_vals(self):
        self.ensure_one()
        product = self.product_id
        product_fee = product.product_fee
        line_vals = {
            "product_id": product_fee.id,
            "quantity": 1.0,
            "move_id": self.move_id.id,
            "account_id": self.account_id.id,
            "analytic_account_id": self.analytic_account_id.id,
        }
        inv_line = self.env["account.move.line"].new(line_vals)
        inv_line.name = product_fee.description_sale or _("Membership initial fee")
        if product.initial_fee == "fixed":
            inv_line.price_unit = product.fixed_fee
        elif product.initial_fee == "percentage":
            inv_line.price_unit = product.percentage_fee * self.price_unit / 100
        return inv_line._convert_to_write(inv_line._cache)

    def initial_fee_create_check(self):
        """
        Inherit this method to implement a custom method
        to decide whether or not to create the initial fee

        :return:
        """
        self.ensure_one()
        product = self.product_id
        if not product or not product.membership or product.initial_fee == "none":
            return False
        # If we are associated to another partner membership, evaluate that
        # partner lines
        partner = self.partner_id.associate_member or self.move_id.partner_id
        # By default, partner to check is the partner of the invoice, but
        # if a special method is found, overwritten in other modules, then
        # the partner is got from that method
        if hasattr(self, "_get_partner_for_membership"):  # pragma: no cover
            partner = self._get_partner_for_membership()
        # See if partner has any membership line to decide whether or not
        # to create the initial fee
        member_lines = self.env["membership.membership_line"].search(
            [
                ("partner", "=", partner.id),
                ("account_invoice_line", "not in", (self.id,)),
                ("state", "not in", ["none", "canceled"]),
            ]
        )
        return not bool(member_lines)

    @api.model_create_multi
    def create(self, vals_list):
        move_lines = super().create(vals_list)
        for move_line in move_lines:
            if move_line.move_id.is_invoice() and move_line.initial_fee_create_check():
                # Charge initial fee
                self.create([move_line._prepare_initial_fee_vals()])
        return move_lines
