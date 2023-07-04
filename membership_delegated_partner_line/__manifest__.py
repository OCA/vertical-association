# Copyright 2023 Graeme Gellatly
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Membership Delegated Partner Line',
    'summary': """
        Adds ability to specify member at invoice line level""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Graeme Gellatly,Odoo Community Association (OCA)',
    'website': 'https://o4sb.com',
    'depends': [
        'membership',
    ],
    'data': [
        'views/account_move.xml',
    ],

}
