# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Product(models.Model):
    """Extend the product template model.
    Added a pricelist_id field to store the associated pricelist.
    Added a product_hierarchy field to store the products that will not be considered.
    """

    _inherit = 'product.template'

    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Associated Pricelist',
        help='Pricelist to add to the member',
        store=True
    )
    product_hierarchy = fields.Many2many(
        'product.template',
        'product_template_membership_rel',
        'product_id',
        'membership_id',
        string='Product Hierarchy',
        domain=[('membership', '=', True)],
        help='Products that will not be considered because current product is better.'
    )

    @api.onchange('product_hierarchy')
    def _check_product_hierarchy(self):
        """Check if current product is already in the product hierarchy."""
        if self.product_hierarchy:
            for product in self.product_hierarchy:
                if self in product.product_hierarchy:
                    raise models.ValidationError(
                        'Current product is already in the product hierarchy of %s' % product.name
                    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Override the default fields view based on context."""
        if self._context.get('product') == 'membership_product':
            if view_type == 'form':
                view_id = self.env.ref('membership.membership_products_form').id
            else:
                view_id = self.env.ref('membership.membership_products_tree').id
        return super(Product, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
