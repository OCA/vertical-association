# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr/).
# @author Damien Horvat <ultrarushgame@gmail.com>
# @author Romain Duciel <romain@mokatourisme.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MembershipLineInherit(models.Model):
    """Extend the membership membership line model."""

    _inherit = "membership.membership_line"

    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist", store=True)
    user_id = fields.Many2one("res.users", string="Users", store=True)

    def _cron_set_default_membership_groups(self):
        """Cron to set default membership groups."""
        lines = self.search(
            [("pricelist_id", "=", False), ("partner.user_ids", "!=", False)]
        )
        for line in lines:
            line.write(
                {"pricelist_id": [(6, 0, line.membership_id.membership_group_ids.ids)]}
            )

    def _cron_update_membership_lines_pricelist(self):
        """Cron to update membership lines according to date and status."""
        today = fields.Date.today()
        lines_to_expired = self.search(
            [("date_to", "<", today), ("state", "in", ["paid", "free", "invoiced"])]
        )
        for line in lines_to_expired:
            line.write({"state": "old"})
        lines_to_begin = self.search(
            [
                ("date_from", "<=", today),
                ("date_to", ">", today),
                ("state", "not in", ["paid", "free"]),
            ]
        )
        for line in lines_to_begin:
            if line.member_price > 0:
                line.write({"state": "paid"})
            elif line.member_price == 0:
                line.write({"state": "free"})

    @api.model
    def write(self, vals):
        """Override write method to handle state changes."""
        res = super(MembershipLineInherit, self).write(vals)
        for record in self:
            if "state" in vals:
                partner = record.partner
                if vals["state"] in ["old", "canceled"]:
                    membership_lines = self.env["membership.membership_line"].search(
                        [
                            ("partner", "=", partner.id),
                            ("state", "in", ["paid", "free"]),
                        ]
                    )
                    membership_lines = membership_lines.filtered(
                        lambda line: record.membership_id.product_tmpl_id
                        not in membership_lines.mapped(
                            "membership_id.product_hierarchy"
                        )
                    )
                    membership_lines = membership_lines.sorted(
                        key=lambda line: line.date_to, reverse=True
                    ).filtered(lambda line: line.date_from <= fields.Date.today())
                    if membership_lines:
                        record.partner.property_product_pricelist = membership_lines[
                            0
                        ].pricelist_id
                    else:
                        default_pricelist_id = (
                            self.env["res.config.settings"]
                            .sudo()
                            .default_get(["default_pricelist_id"])[
                                "default_pricelist_id"
                            ]
                        )
                        record.partner.property_product_pricelist = default_pricelist_id
                elif vals["state"] == "paid":
                    if record.state == "paid":
                        if (
                            record.partner.property_product_pricelist
                            != record.pricelist_id
                        ):
                            record.partner.property_product_pricelist = (
                                record.pricelist_id
                            )
        return res

    @api.depends(
        "account_invoice_id.state",
        "account_invoice_id.amount_residual",
        "account_invoice_id.payment_state",
    )
    def _compute_state(self):
        """Compute state of the membership line."""
        today = fields.Date.today()
        for line in self:
            invoice_state = line.account_invoice_id.state
            payment_state = line.account_invoice_id.payment_state

            if line.member_price <= 0:
                line.state = "none"
                if invoice_state == "draft":
                    line.state = "waiting"
                elif invoice_state == "posted":
                    if payment_state in ("paid", "in_payment"):
                        line.state = "paid"
                    elif payment_state in ("not_paid", "partial"):
                        line.state = "invoiced"
                elif invoice_state == "cancel":
                    line.state = "canceled"
            elif line.state not in ["paid", "old"]:
                if today > line.date_to:
                    line.state = "old"
                elif line.date_from > today:
                    if payment_state == "in_payment":
                        line.state = "waiting"
                    else:
                        line.state = "invoiced"
                elif today <= line.date_to and payment_state == "paid":
                    line.state = "paid"
                elif today <= line.date_to and payment_state != "in_payment":
                    line.state = ""
                if (
                    line.state == "paid"
                    and line.partner.property_product_pricelist != line.pricelist_id
                ):
                    line.partner.property_product_pricelist = line.pricelist_id
            elif line.state == "old" and line.partner.existing_pricelist_id:
                line.partner.property_product_pricelist = (
                    line.partner.existing_pricelist_id
                )

    def create(self, vals):
        """Override create method to set default pricelist."""
        for cell in vals:
            if isinstance(cell, dict) and cell.get("membership_id"):
                product_pricelist_id = (
                    self.env["product.template"]
                    .search([("product_variant_ids", "=", cell["membership_id"])])
                    .pricelist_id.id
                )
                cell["pricelist_id"] = product_pricelist_id
        return super(MembershipLineInherit, self).create(vals)
