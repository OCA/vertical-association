# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MembershipReceipt(models.TransientModel):
    _inherit = "membership.invoice"
    _description = "Membership Receipt"

    def membership_receipt(self):
        receipt_list = (
            self.env["res.partner"]
            .browse(self._context.get("active_ids"))
            .create_membership_receipt(self.product_id, self.member_price)
        )

        search_view_ref = self.env.ref("account.view_account_invoice_filter", False)
        form_view_ref = self.env.ref("account.view_move_form", False)
        tree_view_ref = self.env.ref("account.view_move_tree", False)

        return {
            "domain": [("id", "in", receipt_list.ids)],
            "name": "Membership Receipts",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "views": [(tree_view_ref.id, "tree"), (form_view_ref.id, "form")],
            "search_view_id": search_view_ref and search_view_ref.id,
        }
