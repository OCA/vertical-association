import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-contract_membership_delegated_partner',
        'odoo14-addon-membership_delegated_partner',
        'odoo14-addon-membership_extension',
        'odoo14-addon-membership_initial_fee',
        'odoo14-addon-membership_prorate',
        'odoo14-addon-membership_prorate_variable_period',
        'odoo14-addon-membership_variable_period',
        'odoo14-addon-membership_withdrawal',
        'odoo14-addon-website_membership_random_order',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
