import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-membership_delegated_partner>=15.0dev,<15.1dev',
        'odoo-addon-membership_extension>=15.0dev,<15.1dev',
        'odoo-addon-membership_variable_period>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
