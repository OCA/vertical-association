# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    membership_autoextend = fields.Boolean('Autoextend membership',
                                           default=False)
    membership_autoextend_product_id = fields.Many2one(
        'product.template', string='Extension membership',
        help='If selected, use this product for extensions. Otherwise, the '
        'current membership product will be used.',
        domain=[('membership', '=', True)])
    membership_autoextend_warning_days = fields.Integer(
        'Warn before autoextend', help='The amount of days to send warning '
        'email before automatic extension')
    membership_autoextend_warning_template_id = fields.Many2one(
        'email.template', string='Autoextend warning',
        help='This email is sent the selected amount of days before a '
        'membership was extended',
        domain=[('model_id.model', '=', 'membership.membership_line')])
    membership_autoextend_info_template_id = fields.Many2one(
        'email.template', string='Autoextend info',
        help='This email is sent after a membership was extended',
        domain=[('model_id.model', '=', 'membership.membership_line')])
