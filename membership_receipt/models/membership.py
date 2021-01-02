# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    account_invoice_id = fields.Many2one(string="Document")
