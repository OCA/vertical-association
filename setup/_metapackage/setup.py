import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-membership_autoextend',
        'odoo8-addon-membership_extension',
        'odoo8-addon-membership_initial_fee',
        'odoo8-addon-membership_prorrate',
        'odoo8-addon-membership_prorrate_variable_period',
        'odoo8-addon-membership_variable_period',
        'odoo8-addon-website_membership_contact_visibility',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
