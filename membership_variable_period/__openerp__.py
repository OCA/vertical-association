# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Variable period for memberships',
    'version': '8.0.2.0.0',
    'license': 'AGPL-3',
    'category': 'Association',
    'author': 'Tecnativa, '
              'Antiun Ingeniería S.L., '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org/',
    'depends': [
        'membership_extension',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    "installable": True,
}
