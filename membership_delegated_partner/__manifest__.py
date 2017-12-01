# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Membership Delegate Partner',
    'version': '10.0.1.0.1',
    'category': 'Membership',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/vertical-association',
    'license': 'AGPL-3',
    'summary': 'Delegate membership on a specific partner',
    'depends': [
        'membership',
    ],
    'data': [
        'security/membership_security.xml',
        'views/account_invoice.xml',
    ],
    'installable': True,
}
