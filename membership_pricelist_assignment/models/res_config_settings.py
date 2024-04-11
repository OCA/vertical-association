# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    """Settings for configuring the module. 
    Allows to set the default price list to be used after the end of a membership."""

    _inherit = 'res.config.settings'

    default_pricelist_id = fields.Many2one(
        'product.pricelist',
        default_model='product.pricelist.item',
        default=lambda self: self.env['product.pricelist.item'].search([], limit=1).id,
        help="The default price list to be used after the end of a membership."
    )
