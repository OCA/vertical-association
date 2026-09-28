# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    initial_fee = fields.Selection(
        selection=[
            ("none", "No initial fee"),
            ("fixed", "Fixed amount"),
            ("percentage", "Percentage of the price"),
        ],
        default="none",
        string="Initial fee",
        required=True,
    )
    fixed_fee = fields.Float(
        compute="_compute_fixed_fee", readonly=False, store=True, digits="Product Price"
    )
    percentage_fee = fields.Float(digits=(12, 2), string="Perc. fee (%)")
    product_fee = fields.Many2one(
        comodel_name="product.product",
        string="Product for initial fee",
        domain="[('membership', '=', False)]",
    )

    @api.depends("product_fee.list_price")
    def _compute_fixed_fee(self):
        for template in self:
            template.fixed_fee = template.product_fee.list_price
