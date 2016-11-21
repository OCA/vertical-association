# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Membership withdrawal",
    "summary": "Log membership withdrawal reason and date of request",
    "version": "8.0.1.0.0",
    "category": "Association",
    "website": "https://odoo-community.org/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "membership_extension",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/membership_withdrawal_reason_data.xml",
        "views/membership_withdrawal_reason_view.xml",
        "views/res_partner_view.xml",
    ],
}
