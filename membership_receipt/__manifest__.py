# Copyright 2021 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Membership Receipt",
    "version": "14.0.1.0.0",
    "category": "Vertical Association",
    "summary": "Join membership with sale receipt",
    "author": "Pordenone Linux User Group (PNLUG), Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "license": "AGPL-3",
    "depends": ["membership", "account"],
    "data": [
        "views/account_journal_views.xml",
        "wizard/membership_receipt_views.xml",
    ],
    "installable": True,
    "application": False,
}
