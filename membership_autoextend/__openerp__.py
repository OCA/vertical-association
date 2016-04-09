# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Autoextend membership",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Association",
    "summary": "Extend variable memberships automatically",
    "depends": [
        'membership_variable_period',
        'email_template',
    ],
    "demo": [
        "demo/product_product.xml",
    ],
    "data": [
        "data/email_template.xml",
        "views/res_partner.xml",
        "views/product_template.xml",
    ],
}
