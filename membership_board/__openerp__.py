# -*- coding: utf-8 -*-
# (c) 2015 Incaser Informatica S.L. - Sergio Teruel
# (c) 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Membership Board',
    'summary': 'Management association membership board',
    'version': '8.0.1.0.0',
    'category': "Association",
    'author': 'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['membership'],
    'data': [
        'data/membership_board_data.xml',
        'views/res_company_view.xml',
        'views/membership_board_view.xml',
        'views/membership_board_menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
