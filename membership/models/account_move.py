# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019-2020 Onestein - Andrea Stirpe


from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        # OVERRIDE to write the partner on the membership lines.
        res = super().write(vals)
        if "partner_id" in vals:
            lines = self.invoice_line_ids.membership_line_ids
            if lines:
                lines.write({"partner_id": vals["partner_id"]})
        return res

    def button_draft(self):
        # OVERRIDE to update the cancel date.
        res = super().button_draft()
        for move in self.filtered(lambda x: x.move_type == "out_invoice"):
            lines = move.invoice_line_ids.membership_line_ids
            if lines:
                lines.write({"date_cancel": False, "state": "waiting"})
        return res

    def button_cancel(self):
        # OVERRIDE to update the cancel date.
        # Cancel membership for customer invoices and restore previous
        # membership state for customer refunds. Harmless on supplier ones.
        res = super().button_cancel()
        for move in self.filtered(lambda x: x.move_type == "out_invoice"):
            lines = move.invoice_line_ids.membership_line_ids
            if lines:
                lines.write(
                    {
                        "date_cancel": fields.Date.context_today(self),
                        "state": "canceled",
                    }
                )
        for refund in self.filtered(
            lambda r: r.move_type == "out_refund" and r.reversed_entry_id
        ):
            origin = refund.reversed_entry_id
            lines = origin.mapped("invoice_line_ids.membership_line_ids")
            if lines:
                if origin.payment_state == "reversed":
                    origin_state = "paid"
                else:
                    origin_state = "invoiced"
                lines.filtered(lambda r: r.state == "canceled").write(
                    {"state": origin_state}
                )
                lines.write({"date_cancel": False})
        return res

    def action_post(self):
        # Handle validated refunds for cancelling membership lines
        res = super().action_post()
        self.filtered(lambda m: (m.move_type == "out_invoice")).mapped(
            "invoice_line_ids.membership_line_ids"
        ).write({"state": "invoiced"})
        for refund in self.filtered(
            lambda r: r.move_type == "out_refund" and r.reversed_entry_id
        ):
            origin = refund.reversed_entry_id
            lines = origin.mapped("invoice_line_ids.membership_line_ids")
            if lines:
                if origin.amount_untaxed == refund.amount_untaxed:
                    lines.write(
                        {"state": "canceled", "date_cancel": refund.invoice_date}
                    )
                else:
                    lines.write({"date_cancel": refund.invoice_date})
        return res
