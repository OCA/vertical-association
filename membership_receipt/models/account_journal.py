# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    membership_receipts = fields.Boolean(string="Receipts")

    @api.model
    def get_membership_receipt_journal(self):
        membership_receipt_journal_id = self.search(
            [("type", "=", "sale"), ("membership_receipts", "=", True)], limit=1
        )

        if not membership_receipt_journal_id:
            raise UserError(_("No journal found for membership receipts"))

        return membership_receipt_journal_id
