# Copyright 2023 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": 'Membership Section',
    "description": "Add Sections to the Membership functional area.",
    "category": 'Membership',
    "version": '15.0.1.0.0',
    "author": 'Onestein, Odoo Community Association (OCA)',
    "license": "AGPL-3",
    "website": "https://github.com/OCA/vertical-association",
    "depends": [
        "contacts",
        "membership",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/membership_section_view.xml",
        "views/res_partner_view.xml",
        "menuitems.xml",
    ]
}
