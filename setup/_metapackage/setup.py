import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-contract_membership_delegated_partner',
        'odoo13-addon-membership_delegated_partner',
        'odoo13-addon-membership_extension',
        'odoo13-addon-membership_initial_fee',
        'odoo13-addon-membership_variable_period',
        'odoo13-addon-membership_withdrawal',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
