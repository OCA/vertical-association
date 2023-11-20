# SPDX-FileCopyrightText: 2023 Coop IT Easy, Odoo Community Association (OCA)
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Membership types",
    "summary": """
        A small module that provides the scaffolding for membership types that
        interact differently with membership periods.""",
    "version": "16.0.1.0.0",
    "category": "Association",
    "website": "https://github.com/OCA/vertical-association",
    "author": "Coop IT Easy, Odoo Community Association (OCA)",
    "maintainers": ["carmenbianca"],
    "license": "AGPL-3",
    "application": False,
    "depends": ["membership_extension"],
    "excludes": [],
    "data": ["views/product_template_views.xml"],
    "demo": [],
    "qweb": [],
}
