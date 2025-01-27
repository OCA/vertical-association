# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["res.partner"].search(
        [("membership_last_start", "!=", False)]
    )._compute_membership_date()
