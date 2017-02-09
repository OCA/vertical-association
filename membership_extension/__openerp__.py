# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Membership extension",
    "summary": "Improves user experience of membership addon",
    "version": "8.0.1.0.1",
    "category": "Association",
    "website": "https://odoo-community.org/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "membership",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/membership_category_view.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "data/membership_category_data.xml",
    ],
    "demo": [
        "demo/membership_category_demo.xml",
        "demo/product_template_demo.xml",
    ],
}
