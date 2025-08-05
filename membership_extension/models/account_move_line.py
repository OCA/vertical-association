# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019-2020 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    membership_lines = fields.One2many(
        comodel_name="membership.membership_line", inverse_name="account_invoice_line"
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.move_id.move_type == "out_invoice" and line.product_id.membership:
                line.membership_lines.write({"state": "waiting"})
        return lines

    def unlink(self):
        lines = self.with_context(allow_membership_line_unlink=True)
        return super(AccountMoveLine, lines).unlink()
