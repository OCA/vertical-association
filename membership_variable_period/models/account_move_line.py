# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019-2020 Onestein - Andrea Stirpe
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
import math
from datetime import timedelta

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_membership_line(self, move, product, price_unit, line_id, qty=1.0):
        qty = int(math.ceil(qty))
        date_from = move.invoice_date or fields.Date.today()
        date_to = product.product_tmpl_id._get_next_date(date_from, qty=qty)
        date_to = date_to and (date_to - timedelta(days=1)) or False
        return {
            "partner": move.partner_id.id,
            "membership_id": product.id,
            "member_price": price_unit,
            "date": move.invoice_date or fields.Date.today(),
            "date_from": date_from,
            "date_to": date_to,
            "state": "waiting",
            "account_invoice_line": line_id,
        }

    @api.model
    def _get_variable_period_product_membership_types(self):
        return ["variable"]

    def write(self, vals):
        """Create before the lines of membership with variable period."""
        memb_line_model = self.env["membership.membership_line"]
        if any(x in vals for x in ["product_id", "quantity", "move_id"]):
            membership_types = self._get_variable_period_product_membership_types()
            for line in self:
                product = (
                    self.env["product.product"].browse(vals["product_id"])
                    if vals.get("product_id")
                    else line.product_id
                )
                move = (
                    self.env["account.move"].browse(vals["move_id"])
                    if vals.get("move_id")
                    else line.move_id
                )
                if (
                    move.move_type == "out_invoice"
                    and product.membership
                    and product.membership_type in membership_types
                ):
                    quantity = float(vals.get("quantity", line.quantity))
                    price_unit = vals.get("price_unit", line.price_unit)
                    membership_vals = self._prepare_membership_line(
                        move, product, price_unit, line.id, qty=quantity
                    )
                    if line.membership_lines:
                        if len(line.membership_lines) > 1:  # pragma: no cover
                            # Remove all except last one,
                            # only one membership line per invoice line
                            line.membership_lines[:-1].unlink()
                        # Update with changes
                        line.membership_lines[0].write(membership_vals)
                    else:
                        # Create membership line
                        memb_line_model.create(membership_vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        membership_types = self._get_variable_period_product_membership_types()
        for line in lines.filtered(
            lambda l: l.move_id.move_type == "out_invoice"
            and l.product_id.membership
            and l.product_id.membership_type in membership_types
        ):
            qty = float(line.quantity)
            membership_vals = self._prepare_membership_line(
                line.move_id, line.product_id, line.price_unit, line.id, qty=qty
            )
            # There's already the super line
            line.membership_lines[0].write(membership_vals)
        return lines
