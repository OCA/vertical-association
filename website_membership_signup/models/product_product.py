# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _website_membership_signup_get_products(self):
        return self.sudo().search([
            ('website_published', '=', True),
            ('membership', '=', True),
        ])
