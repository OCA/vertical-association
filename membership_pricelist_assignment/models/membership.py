# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pdb

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import date


class MembershipLineInherit(models.Model):
    """Extend the membership membership line model."""

    _inherit = 'membership.membership_line'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', store=True)
    user_id = fields.Many2one('res.users', string='Users', store=True)

    def _cron_set_default_membership_groups(self):
        """Cron to set default membership groups."""
        print("Cron set default membership groups")
        lines = self.search([('pricelist_id', '=', False), ('partner.user_ids', '!=', False)])
        for line in lines:
            line.write({'pricelist_id': [(6, 0, line.membership_id.membership_group_ids.ids)]})

    def _cron_update_membership_lines_pricelist(self):
        """Cron to update membership lines according to date and status."""
        default_pricelist_id = self.env['res.config.settings'].sudo().default_get(['default_pricelist_id'])['default_pricelist_id']
        print("Default Pricelist:", default_pricelist_id)
        today = fields.Date.today()
        lines_to_expired = self.search([('date_to', '<', today), ('state', 'in', ['paid', 'free', 'invoiced'])])
        print("Lines to expire: ", lines_to_expired)
        for line in lines_to_expired:
            line.write({'state': 'old'})
        lines_to_begin = self.search([('date_from', '<=', today), ('date_to', '>', today), ('state', 'not in', ['paid', 'free'])])
        for line in lines_to_begin:
            if line.member_price > 0:
                print("Line: ", line)
                line.write({'state': 'paid'})
            elif line.member_price == 0:
                line.write({'state': 'free'})

    @api.model
    def write(self, vals):
        """Override write method to handle state changes."""
        print("on write")
        res = super(MembershipLineInherit, self).write(vals)
        for record in self:
            print("record: ", record)
            if "state" in vals:
                partner = record.partner
                print("state: ", vals["state"], "\n", "record.partner: ", record.partner)
                if vals["state"] in ['old', 'canceled']:
                    print("partner: ", partner)
                    membership_lines = self.env['membership.membership_line'].search([('partner', '=', partner.id), ('state', 'in', ['paid', 'free'])])
                    membership_lines = membership_lines.filtered(lambda line: record.membership_id.product_tmpl_id not in membership_lines.mapped('membership_id.product_hierarchy'))
                    membership_lines = membership_lines.sorted(key=lambda line: line.date_to, reverse=True).filtered(lambda line: line.date_from <= fields.Date.today())
                    if membership_lines:
                        record.partner.property_product_pricelist = membership_lines[0].pricelist_id
                    else:
                        default_pricelist_id = self.env['res.config.settings'].sudo().default_get(['default_pricelist_id'])['default_pricelist_id']
                        print("Default Pricelist:", default_pricelist_id)
                        record.partner.property_product_pricelist = default_pricelist_id
                elif vals["state"] == 'paid':
                    print("Setting pricelist and state for ", record.partner)
                    if record.state == 'paid':
                        if record.partner.property_product_pricelist != record.pricelist_id:
                            record.partner.property_product_pricelist = record.pricelist_id
        return res

    @api.depends('account_invoice_id.state', 'account_invoice_id.amount_residual', 'account_invoice_id.payment_state')
    def _compute_state(self):
        """Compute state of the membership line."""
        print("Compute state")
        today = fields.Date.today()
        for line in self:
            print("Line: ", line)
            move_state = line.account_invoice_id.state
            payment_state = line.account_invoice_id.payment_state

            if line.member_price > 0 and line.state not in ['paid', 'old']:
                if line.date_from <= today <= line.date_to and payment_state == 'paid':
                    line.state = 'paid'
                elif today > line.date_to:
                    line.state = 'old'
                elif line.date_from > today:
                    if line.account_invoice_id.payment_state == 'in_payment':
                        line.state = 'waiting'
                    else:
                        line.state = 'invoiced'
                elif line.date_from <= today <= line.date_to and payment_state != 'in_payment':
                    line.state = ''
            else:
                print("Line state: ", line.state)
                line.state = 'none'
                if move_state == 'draft':
                    line.state = 'waiting'
                elif move_state == 'posted':
                    print("Move state posted and payment state: ", payment_state)
                    if payment_state == 'paid':
                        line.state = 'paid'
                    elif payment_state == 'in_payment':
                        print("In payment")
                        line.state = 'paid'
                    elif payment_state in ('not_paid', 'partial'):
                        print("Not paid or partial")
                        line.state = 'invoiced'
                elif move_state == 'cancel':
                    line.state = 'canceled'
            if line.date_to < today:
                line.state = 'old'
            if line.state == 'paid':
                if line.partner.property_product_pricelist != line.pricelist_id:
                    line.partner.property_product_pricelist = line.pricelist_id
            elif line.partner.existing_pricelist_id and line.state == 'old':
                line.partner.property_product_pricelist = line.partner.existing_pricelist_id

    def create(self, vals):
        """Override create method to set default pricelist."""
        for cell in vals:
            print("Cell: ", cell)
            if cell['membership_id']:
                product_pricelist_id = self.env['product.template'].search([('product_variant_ids', '=', cell['membership_id'])]).pricelist_id.id
                cell['pricelist_id'] = product_pricelist_id
            print("Vals: ", vals)
        return super(MembershipLineInherit, self).create(vals)
