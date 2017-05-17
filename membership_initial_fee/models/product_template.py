# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingenieria S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    initial_fee = fields.Selection(
        selection=[('none', 'No initial fee'),
                   ('fixed', 'Fixed amount'),
                   ('percentage', 'Percentage of the price')],
        default='none', string="Initial fee", required=True)
    fixed_fee = fields.Float(digits=dp.get_precision('Product Price'))
    percentage_fee = fields.Float(digits=(12, 2), string="Perc. fee (%)")
    product_fee = fields.Many2one(
        comodel_name='product.product', string="Product for initial fee",
        domain="[('membership', '=', False)]")

    @api.onchange('product_fee')
    def onchange_product_fee(self):
        self.fixed_fee = self.product_fee.list_price
