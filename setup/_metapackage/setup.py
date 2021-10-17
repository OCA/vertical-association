import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-contract_membership_delegated_partner',
        'odoo11-addon-membership_delegated_partner',
        'odoo11-addon-membership_extension',
        'odoo11-addon-membership_initial_fee',
        'odoo11-addon-membership_product_set',
        'odoo11-addon-membership_prorate',
        'odoo11-addon-membership_prorate_variable_period',
        'odoo11-addon-membership_variable_period',
        'odoo11-addon-membership_withdrawal',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
