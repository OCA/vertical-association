# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Prorrate membership fee',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Association',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'depends': [
        'membership',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
}
