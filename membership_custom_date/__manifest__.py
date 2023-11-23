# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Custom date for memberships",
    "summary": """
        Memberships with custom dates have their dates specified on a
        subscription-by-subscription basis.""",
    "version": "16.0.1.0.0",
    "category": "Association",
    "website": "https://github.com/OCA/vertical-association",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "maintainers": ["carmenbianca"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "membership_extension",
        "membership_type",
    ],
    "excludes": [],
    "data": [
        "views/product_template_views.xml",
        "wizard/membership_invoice_views.xml",
    ],
    "demo": [],
    "qweb": [],
}
