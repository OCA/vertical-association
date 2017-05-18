# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    membership_lines = fields.One2many(
        comodel_name='membership.membership_line',
        inverse_name='account_invoice_line')

    @api.model
    def create(self, vals):
        line = super(AccountInvoiceLine, self).create(vals)
        if (line.invoice_id.type == 'out_invoice' and
                line.product_id.membership):
            line.membership_lines.write({
                'state': 'waiting',
            })
        return line

    @api.multi
    def unlink(self):
        lines = self.with_context(allow_membership_line_unlink=True)
        return super(AccountInvoiceLine, lines).unlink()
