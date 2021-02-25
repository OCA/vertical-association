# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "contract.contract"

    delegated_member_id = fields.Many2one(
        comodel_name="res.partner", string="Delegated Member",
    )

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super()._prepare_invoice(
            date_invoice, journal=journal
        )
        invoice_vals["delegated_member_id"] = self.delegated_member_id.id
        return invoice_vals, move_form
