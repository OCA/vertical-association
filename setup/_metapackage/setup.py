import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-membership_delegated_partner',
        'odoo12-addon-membership_extension',
        'odoo12-addon-membership_prorate',
        'odoo12-addon-membership_variable_period',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
