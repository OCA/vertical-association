# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Variable period for memberships',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Association',
    'author': 'Antiun Ingeniería S.L., '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'depends': [
        'membership',
    ],
    'data': [
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'data/membership_data.xml',
    ],
    "installable": True,
}
