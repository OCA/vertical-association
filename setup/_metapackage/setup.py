import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-contract_membership_delegated_partner>=16.0dev,<16.1dev',
        'odoo-addon-membership_delegated_partner>=16.0dev,<16.1dev',
        'odoo-addon-membership_extension>=16.0dev,<16.1dev',
        'odoo-addon-membership_initial_fee>=16.0dev,<16.1dev',
        'odoo-addon-membership_prorate>=16.0dev,<16.1dev',
        'odoo-addon-membership_prorate_variable_period>=16.0dev,<16.1dev',
        'odoo-addon-membership_variable_period>=16.0dev,<16.1dev',
        'odoo-addon-membership_withdrawal>=16.0dev,<16.1dev',
        'odoo-addon-website_membership_gamification>=16.0dev,<16.1dev',
        'odoo-addon-website_membership_random_order>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
