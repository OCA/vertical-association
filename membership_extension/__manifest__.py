# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2017 Luis M. Ontalba <luis.martinez@tecnativa.com>
# Copyright 2017-2018 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Membership extension",
    "summary": "Improves user experience of membership addon",
    "version": "16.0.1.0.1",
    "category": "Membership",
    "author": "Tecnativa, Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["membership"],
    "data": [
        "security/membership_security.xml",
        "security/ir.model.access.csv",
        "views/membership_category_view.xml",
        "views/membership_views.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "data/membership_category_data.xml",
    ],
    "demo": [
        "demo/membership_category_demo.xml",
        "demo/product_template_demo.xml",
        "demo/membership_security_demo.xml",
    ],
}
