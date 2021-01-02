# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = "res.partner"

    def create_membership_receipt(self, product, amount):
        """Create Receipt of Membership for partners."""
        receipt_vals_list = []
        for partner in self:
            addr = partner.address_get(["invoice"])
            if partner.free_member:
                raise UserError(_("Partner is a free Member."))
            if not addr.get("invoice", False):
                raise UserError(
                    _("Partner doesn't have an address to make the receipt.")
                )

            receipt_vals_list.append(
                {
                    "move_type": "out_receipt",
                    "partner_id": partner.id,
                    "invoice_line_ids": [
                        (
                            0,
                            None,
                            {
                                "product_id": product.id,
                                "quantity": 1,
                                "price_unit": amount,
                                "tax_ids": [(6, 0, product.taxes_id.ids)],
                            },
                        )
                    ],
                }
            )

        return self.env["account.move"].create(receipt_vals_list)
