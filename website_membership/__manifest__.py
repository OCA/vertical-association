# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Online Members Directory",
    "summary": "Publish your members directory",
    "version": "19.0.1.0.0",
    "category": "Membership",
    "author": "Odoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "depends": ["website_partner", "website_google_map", "membership", "website_sale"],
    "data": [
        "views/product_template_views.xml",
        "views/website_membership_templates.xml",
        "security/ir.model.access.csv",
        "security/website_membership.xml",
    ],
    "demo": ["demo/membership_demo.xml"],
    "installable": True,
    "license": "LGPL-3",
    "assets": {
        "website.website_builder_assets": [
            "website_membership/static/src/website_builder/**/*",
        ],
    },
}
