# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    "name": "Members",
    "version": "19.0.1.1.0",
    "category": "Membership",
    "development_status": "Mature",
    "author": "Odoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/membership_invoice_views.xml",
        "data/membership_data.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        "report/report_membership_views.xml",
    ],
    "license": "LGPL-3",
}
