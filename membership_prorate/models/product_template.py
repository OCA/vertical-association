# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_prorate = fields.Boolean(
        string="Prorate",
        help="If this check is marked, then the fee will be proportionally "
        "charged for the remaining time of the period",
    )
