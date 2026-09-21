# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017-18 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import timedelta

from odoo import api, fields, models
from odoo.tests import Form


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

    def _prepare_invoice_line_prorate_vals(self, invoice_line):
        product = invoice_line.product_id
        date_invoice = invoice_line.move_id.invoice_date or fields.Date.today()
        date_from, date_to = self._get_membership_interval(product, date_invoice)
        if not date_from:
            return {
                "quantity": 1.0,
                "date_from": date_invoice,
            }
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

    @api.model_create_multi
    def create(self, vals_list):
        invoice_lines = super().create(vals_list)
        for invoice_line in invoice_lines.filtered(
            lambda r: r.product_id.membership and r.product_id.membership_prorate
        ):
            # Change quantity accordingly the prorate
            invoice_line_vals = self._prepare_invoice_line_prorate_vals(invoice_line)
            if invoice_line_vals:
                date_from = invoice_line_vals["date_from"]
                quantity = invoice_line_vals["quantity"]
                invoice = invoice_line.move_id
                with Form(invoice) as invoice_form:
                    index = next(
                        (
                            index
                            for (index, d) in enumerate(
                                invoice_form.invoice_line_ids._records
                            )
                            if d["id"] == invoice_line.id
                        ),
                        None,
                    )
                    if index is not None:
                        with invoice_form.invoice_line_ids.edit(index) as line_form:
                            line_form.quantity = quantity
                # Rectify membership price and start date in this case
                memb_line = self.env["membership.membership_line"].search(
                    [("account_invoice_line", "=", invoice_line.id)], limit=1
                )
                memb_line.write(
                    {
                        "member_price": invoice_line.price_subtotal,
                        "date_from": date_from,
                    }
                )
        return invoice_lines
