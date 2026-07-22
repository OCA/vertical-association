# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

renamed_fields = [
    (
        "membership.membership_line",
        "membership_membership_line",
        "partner",
        "partner_id",
    ),
    (
        "membership.membership_line",
        "membership_membership_line",
        "account_invoice_line",
        "account_invoice_line_id",
    ),
    (
        "res.partner",
        "res_partner",
        "member_lines",
        "member_line_ids",
    ),
    (
        "res.partner",
        "res_partner",
        "associate_member",
        "associate_member_id",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
