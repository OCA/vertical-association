# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr/).
# @author Damien Horvat <ultrarushgame@gmail.com>
# @author Romain Duciel <romain@mokatourisme.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Membership Pricelist Assignment",
    "version": "16.0.1.0.1",
    "category": "Membership",
    "author": "Moka, Odoo Community Association (OCA)",
    "summary": "Membership Pricelist Assignment",
    "depends": ["membership", "base_setup"],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "data": [
        "views/res_config_settings_views.xml",
        "views/product_views.xml",
        "views/membership_views.xml",
        "data/membership_data.xml",
    ],
}
