# Copyright 2019 Yu Weng <yweng@elegosoft.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_set = fields.Boolean(
        help="Check if the product is eligible for membership set.",
        string="Membership set")
    membership_set_products = fields.Many2many(
        'product.product',
        'membership_set_products_rel',
        'membership_set_id',
        'product_id',
        string="Membership products")
