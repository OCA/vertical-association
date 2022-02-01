# Copyright 2021 Manuel Calero <manuelcalero@xtendoo.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Membership sisterhood",
    "summary": "Improves user experience of membership addon",
    "version": "14.0.1.0.0",
    "category": "Membership",
    "author": "Xtendoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["membership_extension"],
    "data": [
        "views/res_partner_view.xml",
    ],
}
