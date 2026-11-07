# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019-2020 Onestein - Andrea Stirpe

from datetime import date

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    membership = fields.Boolean(related="product_id.membership")
    membership_line_ids = fields.One2many(
        "membership.membership_line",
        "account_invoice_line_id",
        string="Membership lines",
    )

    # -------------------------------------------------
    # CRUD
    # -------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._do_membership_lines()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self._do_membership_lines()
        return res

    def unlink(self):
        lines = self.with_context(allow_membership_line_unlink=True)
        return super(AccountMoveLine, lines).unlink()

    # -------------------------------------------------
    # Business Logics
    # -------------------------------------------------
    def _do_membership_lines(self):
        to_create = self._filter_membership_lines()
        to_create._create_membership_lines()

    def _filter_membership_lines(self):
        MoveLine = self.env["account.move.line"]
        to_create = MoveLine
        for line in self:
            if line.move_id.move_type != "out_invoice":
                continue
            if line.membership:
                to_create |= line
        return to_create

    def _create_membership_lines(self):
        """
        Common case: a new invoice is created with lines using membership product.
        Let's create the membership lines.
        """
        vals_list = [line._prepare_membership_line_vals() for line in self]
        return self.env["membership.membership_line"].create(vals_list)

    def _prepare_membership_line_vals(self):
        self.ensure_one()
        invoice = self.move_id
        date_from, date_to = self._prepare_membership_line_dates()
        return {
            "partner_id": invoice.partner_id.id,
            "membership_id": self.product_id.id,
            "member_price": self.price_unit,
            "date": invoice.invoice_date or fields.Date.context_today(self),
            "date_from": date_from,
            "date_to": date_to,
            "account_invoice_line_id": self.id,
        }

    def _prepare_membership_line_dates(self):
        """Extension hook (module membership_variable_period)"""
        self.ensure_one()
        date_from = self.product_id.membership_date_from
        date_to = self.product_id.membership_date_to
        if date_from and date_from < (self.move_id.invoice_date or date.min) < (
            date_to or date.min
        ):
            date_from = self.move_id.invoice_date
        return (date_from, date_to)
