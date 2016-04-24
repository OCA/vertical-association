# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _website_partner_signup_get_default_value(self, field_name):
        if field_name == 'country_id':
            return self.env['res.country'].sudo().search([
                ('code', '=', self.env.context.get('lang', 'en_US')
                 .split('_')[-1]),
            ])[:1].id

    @api.model
    def _website_partner_signup_fields_blacklist(self):
        """return fields to never accept for creating partners via website"""
        return [
            'property_account_receivable', 'property_account_payable',
            'credit_limit', 'user_ids',
        ]

    @api.model
    def _website_partner_signup_validate(self, data):
        """Validate data a user filled into the partner signup form. Return
        a dictionary of error messages if applicable"""
        errors = {}
        for key, value in data.iteritems():
            if key in self._fields and self._fields[key].required and\
                    not value:
                errors[key] = _('Required field!')
        if 'acc_number' in data and not data['acc_number']:
            errors['acc_number'] = _('Required field!')
        return errors

    @api.model
    def _website_partner_signup_prepare(self, data):
        """Do whatever needs to be done to create a partner with this
        function's return value"""
        result = {
            key: value
            for key, value in data.iteritems()
            if key in self._fields and
            key not in self._website_partner_signup_fields_blacklist()
        }
        if 'acc_number' in data:
            bank_values = {
                'state': 'iban' if 'iban' in self.env['res.partner.bank']
                else 'bank',
                'acc_number': data['acc_number'],
            }
            if data.get('bank_bic'):
                bank_values['bank_bic'] = data['bank_bic']
                bank_values['bank'] = self.env['res.bank'].sudo().search([
                    ('bic', '=ilike', data['bank_bic']),
                ]).id
            result['bank_ids'] = [(0, 0, bank_values)]
        return result

    @api.model
    @api.returns('self')
    def _website_partner_signup_create(self, data):
        """Create and return a partner based on data"""
        return self.sudo().create(data)
