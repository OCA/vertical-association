# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Membership extra info",
    "summary": "Extra information about member partners",
    "version": "8.0.1.0.0",
    "category": "Association",
    "website": "http://www.antiun.com",
    "author": "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "membership",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/membership_category_views.xml",
        "views/membership_decline_reason_views.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        "wizards/membership_decline_reason_wizard.xml",
    ],
    "demo": [
        "demo/membership_category_demo.xml",
        "demo/membership_decline_reason_demo.xml",
    ],
}
