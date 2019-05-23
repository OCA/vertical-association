# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    delegated_member_id = fields.Many2one(
        comodel_name='res.partner',
        string='Delegated Member',
    )

    def write(self, vals):
        """Change associated membership lines if delegated member is changed.
        """
        membership_lines = self.mapped('invoice_line_ids').filtered(
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

    @api.model
    def create(self, vals):
        """Sets the delegated partner in out refunds
        """
        if vals.get('type') == 'out_refund' and vals.get('refund_invoice_id'):
            refund_inv = self.browse(vals['refund_invoice_id'])
            if refund_inv.delegated_member_id:
                vals['delegated_member_id'] = refund_inv.delegated_member_id.id
        return super(AccountInvoice, self).create(vals)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _get_partner_for_membership(self):
        """Auxiliary method for getting the correct membership partner for
        certain operations like initial fee check.
        """
        self.ensure_one()
        invoice = self.invoice_id
        return invoice.delegated_member_id or invoice.partner_id
