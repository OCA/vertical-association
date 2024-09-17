# Copyright 2024 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Membership Sale Prorate",
    "summary": "Calculates and sets the quantity for sale order lines having "
    "prorate membership products so that the sale order line price "
    "is calculated accordingly",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Association",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "depends": [
        "membership",
        "membership_prorate",
        "sale",
    ],
    "data": [],
    "auto_install": True,
}
