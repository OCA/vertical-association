# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MembershipLine(models.Model):
    _inherit = 'membership.membership_line'

    @api.model
    def create(self, vals):
        """ Delegate the member line to the designated partner """
        if 'account_invoice_line' not in vals:
            return super(MembershipLine, self).create(vals)
        line = self.env['account.invoice.line'].browse(
            vals['account_invoice_line'])
        if line.invoice_id.delegated_member_id:
            vals['partner'] = line.invoice_id.delegated_member_id.id
        return super(MembershipLine, self).create(vals)
