# -*- coding: utf-8 -*-
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Variable period for memberships',
    'version': '11.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Association',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/vertical-association',
    'depends': [
        'membership_extension',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    "installable": True,
}
