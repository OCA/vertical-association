# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, http
from openerp.http import request


class Main(http.Controller):
    @http.route('/membership/sign_up', type='http', auth='public',
                website=True)
    def sign_up(self, **kwargs):
        errors = request.env['res.partner']._website_partner_signup_validate(
            kwargs)
        if 'product_id' not in kwargs:
            errors['product_id'] = _('Required field!')
        if not errors:
            values = request.env['res.partner'].\
                _website_partner_signup_prepare(kwargs)
            partner = request.env['res.partner']\
                ._website_partner_signup_create(values)
            partner.create_membership_invoice(
                product_id=int(kwargs['product_id']), datas={
                    'amount': request.env['product.product'].sudo().browse(
                        int(kwargs['product_id'])
                    ).list_price,
                })
            request.env['account.invoice'].sudo().search([
                ('partner_id', '=', partner.id),
            ]).signal_workflow('invoice_open')
            return request.render(
                'website_membership_signup.thankyou', qcontext={
                    'data': kwargs,
                    'partner': partner,
                })
        return request.render(
            'website_membership_signup.signup', qcontext={
                'errors': errors,
                'data': kwargs,
            })
