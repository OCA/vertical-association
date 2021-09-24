# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2017-2018 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2019-2020 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_draft(self):
        res = super().button_draft()
        self.filtered(lambda m: m.move_type == "out_invoice").mapped(
            "invoice_line_ids.membership_lines"
        ).write({"state": "waiting"})
        return res

    def button_cancel(self):
        """Cancel membership for customer invoices and restore previous
        membership state for customer refunds. Harmless on supplier ones.
        """
        res = super().button_cancel()
        self.filtered(lambda m: (m.move_type == "out_invoice")).mapped(
            "invoice_line_ids.membership_lines"
        ).write({"state": "canceled"})
        for refund in self.filtered(
            lambda r: r.move_type == "out_refund" and r.reversed_entry_id
        ):
            origin = refund.reversed_entry_id
            lines = origin.mapped("invoice_line_ids.membership_lines")
            if lines:
                origin_state = "paid" if origin.payment_state == "paid" else "invoiced"
                lines.filtered(lambda r: r.state == "canceled").write(
                    {"state": origin_state}
                )
                lines.write({"date_cancel": False})
        return res

    def post(self):
        """Handle validated refunds for cancelling membership lines """
        res = super().post()
        self.filtered(lambda m: (m.move_type == "out_invoice")).mapped(
            "invoice_line_ids.membership_lines"
        ).write({"state": "invoiced"})
        for refund in self.filtered(
            lambda r: r.move_type == "out_refund" and r.reversed_entry_id
        ):
            origin = refund.reversed_entry_id
            lines = origin.mapped("invoice_line_ids.membership_lines")
            if lines:
                if origin.amount_untaxed == refund.amount_untaxed:
                    lines.write(
                        {"state": "canceled", "date_cancel": refund.invoice_date}
                    )
                else:
                    lines.write({"date_cancel": refund.invoice_date})
        return res
