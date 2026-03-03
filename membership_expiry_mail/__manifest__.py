# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Membership Expiry Mail",
    "summary": "Send a mail to members whose membership will expire in a month.",
    "version": "16.0.1.0.0",
    "category": "Association",
    "website": "https://github.com/OCA/vertical-association",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "maintainers": ["mihien"],
    "license": "AGPL-3",
    "depends": [
        "mail",
        "membership",
    ],
    # Please remove empty values below.
    "data": [
        "data/ir_cron.xml",
        "data/membership_expiry_mail.xml",
    ],
    "demo": [],
}
