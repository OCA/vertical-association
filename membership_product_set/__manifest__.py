# Copyright 2019 Yu Weng <yweng@elegosoft.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Set for memberships',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Association',
    'author': 'Yu Weng, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/vertical-association',
    'depends': [
        'membership',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    "installable": True,
}
