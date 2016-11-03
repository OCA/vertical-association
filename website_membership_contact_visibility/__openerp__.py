# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Website Membership Contact Visibility',
    'version': '9.0.1.0.0',
    'summary': 'Adding functionality to set '
               'the visibility of contact information of each member',
    'author': 'OpenSynergy Indonesia,Odoo Community Association (OCA)',
    'website': 'https://opensynergy-indonesia.com',
    'category': 'Website',
    'depends': ['website_membership'],
    'data': [
        'views/res_partner_view.xml',
        'views/website_membership.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
