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
        for line in self:
            line._compute_membership_state()

    def _compute_membership_state(self):
        """Compute membership state based on invoice and payment states."""
        today = fields.Date.today()
        invoice_state = self.account_invoice_id.state
        payment_state = self.account_invoice_id.payment_state
        if payment_state == "paid" and today >= self.date_to:
            self.state = "old"
        elif self.member_price <= 0:
            self._compute_membership_state_free_member(invoice_state, payment_state)
        else:
            self._compute_membership_state_paid_member(
                invoice_state, payment_state, today
            )

    def _compute_membership_state_free_member(self, invoice_state, payment_state):
        """Compute membership state for free members."""
        if invoice_state == "draft":
            self.state = "waiting"
        elif invoice_state == "posted":
            if payment_state in ("paid", "in_payment"):
                self.state = "paid"
            elif payment_state in ("not_paid", "partial"):
                self.state = "invoiced"
        elif invoice_state == "cancel":
            self.state = "canceled"

    def _compute_membership_state_paid_member(
        self, invoice_state, payment_state, today
    ):
        """Compute membership state for paid members."""
        if today >= self.date_to:
            self.state = "old"
        elif self.date_from > today:
            if payment_state == "in_payment":
                self.state = "waiting"
            else:
                self.state = "invoiced"
        elif today <= self.date_to and payment_state == "paid":
            self.state = "paid"
        elif today <= self.date_to and payment_state != "in_payment":
            self.state = ""

        if (
            self.state == "paid"
            and self.partner.property_product_pricelist != self.pricelist_id
        ):
            self.partner.property_product_pricelist = self.pricelist_id

        if self.state == "old" and self.partner.existing_pricelist_id:
            self.partner.property_product_pricelist = self.partner.existing_pricelist_id

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
