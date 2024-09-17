# Copyright 2024 Onestein (<http://www.onestein.eu>)
from datetime import timedelta

from odoo import api, fields, models
from odoo.tests import Form


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_sale_line_prorate_vals(self, sale_line):
        product = sale_line.product_id
        date_order = (
            sale_line.order_id.date_order
            and sale_line.order_id.date_order.date()
            or fields.Date.today()
        )
        date_from, date_to = self.env["account.move.line"]._get_membership_interval(
            product, date_order
        )
        if not date_from:
            return {"quantity": 1.0}
        if date_order < date_from:
            date_order = date_from
        if date_order > date_to:
            date_order = date_to
        theoretical_duration = date_to - date_from + timedelta(1)
        real_duration = date_to - date_order + timedelta(1)
        if theoretical_duration != real_duration:
            return {
                "quantity": round(
                    float(real_duration.days) / theoretical_duration.days, 2
                ),
            }

    @api.model_create_multi
    def create(self, vals_list):
        sale_lines = super().create(vals_list)
        for sale_line in sale_lines.filtered(
            lambda r: r.product_id.membership and r.product_id.membership_prorate
        ):
            # Change quantity accordingly the prorate
            sale_line_vals = self._prepare_sale_line_prorate_vals(sale_line)
            if sale_line_vals:
                quantity = sale_line_vals["quantity"]
                order = sale_line.order_id
                with Form(order) as sale_form:
                    index = next(
                        (
                            index
                            for (index, d) in enumerate(sale_form.order_line._records)
                            if d["id"] == sale_line.id
                        ),
                        None,
                    )
                    if index is not None:
                        with sale_form.order_line.edit(index) as line_form:
                            line_form.product_uom_qty = quantity
        return sale_lines
