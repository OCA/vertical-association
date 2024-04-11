# -*- coding: utf-8 -*-
{
    'name': 'Membership Pricelist Assignment',
    'version': '15.0.1.0.1',
    'category': 'Membership',
    'author': 'Moka',
    'summary': 'Membership Pricelist Assignment',
    'description': "Organize membership pricelist assignment",
    'depends': ['membership', 'base_setup'],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    "data": [
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'views/membership_views.xml',
        'data/membership_data.xml',
    ]
}
