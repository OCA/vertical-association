# -*- coding: utf-8 -*-
# © 2016 Michael Viriyananda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Website Membership Contact Visibility',
    'version': '8.0.1.0.0',
    'summary': 'Adding functionality to set '
               'the visibility of contact information of each member',
    'author': 'Michael Viriyananda,Odoo Community Association (OCA)',
    'website': 'https://github.com/mikevhe18',
    'category': 'Website',
    'depends': ['website_membership'],
    'data': [
        'views/membership_view.xml',
        'views/website_membership.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
