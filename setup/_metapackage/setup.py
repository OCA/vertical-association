import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-contract_membership_delegated_partner',
        'odoo10-addon-membership_delegated_partner',
        'odoo10-addon-membership_extension',
        'odoo10-addon-membership_initial_fee',
        'odoo10-addon-membership_prorrate',
        'odoo10-addon-membership_prorrate_variable_period',
        'odoo10-addon-membership_variable_period',
        'odoo10-addon-membership_withdrawal',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
