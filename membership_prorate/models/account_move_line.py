# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017-18 Tecnativa - David Vidal
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0
from datetime import timedelta

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_membership_interval(self, product, date):
        """Get the interval to evaluate as the theoretical membership period.
        :param product: Product that defines the membership
        :param date: date object for the requested date (if needed for
        inherited computations)
        :return: A tuple with 2 date objects with the beginning and the
        end of the period
        """
        date_from = product.membership_date_from
        date_to = product.membership_date_to
        return date_from, date_to

    def _prepare_invoice_line_prorate_vals(self, product, move):
        date_invoice = move.invoice_date or fields.Date.today()
        date_from, date_to = self._get_membership_interval(product, date_invoice)
        if date_invoice < date_from:
            date_invoice = date_from
        if date_invoice > date_to:
            date_invoice = date_to
        theoretical_duration = date_to - date_from + timedelta(1)
        real_duration = date_to - date_invoice
        if theoretical_duration != real_duration:
            return {
                "quantity": round(
                    float(real_duration.days) / theoretical_duration.days, 2
                ),
                "date_from": date_invoice,
            }
        return {}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = self.env["product.product"].browse(vals.get("product_id", False))
            move = self.env["account.move"].browse(vals["move_id"])
            if product.membership and product.membership_prorate:
                invoice_line_vals = self._prepare_invoice_line_prorate_vals(
                    product, move
                )
                if "quantity" in invoice_line_vals:
                    vals["quantity"] = invoice_line_vals["quantity"]
        move_lines = super().create(vals_list)
        for line in move_lines.filtered(
            lambda l: l.product_id.membership and l.product_id.membership_prorate
        ):
            # Change quantity accordingly the prorate
            invoice_line_vals = self._prepare_invoice_line_prorate_vals(
                line.product_id, line.move_id
            )
            if "date_from" in invoice_line_vals:
                # Rectify membership price and start date in this case
                memb_line = self.env["membership.membership_line"].search(
                    [("account_invoice_line", "=", line.id)], limit=1
                )
                memb_line.write(
                    {
                        "member_price": line.price_subtotal,
                        "date_from": invoice_line_vals["date_from"],
                    }
                )
        return move_lines
