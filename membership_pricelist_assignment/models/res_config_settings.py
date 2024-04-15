# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr/).
# @author Damien Horvat <ultrarushgame@gmail.com>
# @author Romain Duciel <romain@mokatourisme.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Settings for configuring the module.
    Allows to set the default price list to be used after the end of a membership."""

    _inherit = "res.config.settings"

    default_pricelist_id = fields.Many2one(
        "product.pricelist",
        default_model="product.pricelist.item",
        default=lambda self: self.env["product.pricelist.item"].search([], limit=1).id,
        help="The default price list to be used after the end of a membership.",
    )
