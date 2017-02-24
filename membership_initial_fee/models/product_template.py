# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingenieria S.L. - Pedro M. Baeza
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

INITIAL_FEE = [('none', 'No initial fee'),
               ('fixed', 'Fixed amount'),
               ('percentage', 'Percentage of the price')]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    initial_fee = fields.Selection(INITIAL_FEE, default='none', 
                                   string="Initial fee", required=True)
    fixed_fee = fields.Float(digits_compute=dp.get_precision('Product Price'))
    percentage_fee = fields.Float(digits=(12, 2), string="Perc. fee (%)")
    product_fee = fields.Many2one('product.product', 
                                  string='Product for initial fee', 
                                  domain=[('membership', '=', False)])
    
    @api.onchange('product_fee')
    def _onchange_product_fee(self):
        self.fixed_fee = self.product_fee.list_price
