# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    domain = "['|',('company_id','=',False),('company_id','in',company_ids)]"
    rule = env.ref(
        "membership_extension.membership_category_comp_rule", raise_if_not_found=False,
    )
    if rule:
        rule.write({"domain_force": domain})
