# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Membership Delegate Partner",
    "version": "16.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Membership",
    "author": "Tecnativa, Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "license": "AGPL-3",
    "summary": "Delegate membership on a specific partner",
    "depends": ["membership"],
    "data": ["security/membership_security.xml", "views/account_move.xml"],
    "installable": True,
}
