# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    delegated_member_id = fields.Many2one(
        comodel_name='res.partner',
        string='Delegated Member',
    )

    def write(self, vals):
        membership_lines = self.invoice_line_ids.filtered(
            lambda x: x.product_id.membership)
        if 'delegated_member_id' not in vals or not membership_lines:
            return super(AccountInvoice, self).write(vals)
        for line in membership_lines:
            member_line = self.env['membership.membership_line'].search(
                [('account_invoice_line', '=', line.id)])
            if member_line:
                member_line.partner = self.env['res.partner'].browse(
                    vals['delegated_member_id'])
        return super(AccountInvoice, self).write(vals)
