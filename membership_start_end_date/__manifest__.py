# Copyright 2026 Akretion (http://www.akretion.com).
# @author Arnaud LAYEC <arnaud.layec@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Membership Account Start End Dates",
    "version": "18.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/oca-custom",
    "license": "AGPL-3",
    "category": "Membership",
    "depends": [
        "membership_extension",
        "account_invoice_start_end_dates",
    ],
    "data": ["views/membership_line.xml"],
    "installable": True,
    "application": False,
    "development_status": "Alpha",
}
