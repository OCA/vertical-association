import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-vertical-association",
    description="Meta package for oca-vertical-association Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-membership_delegated_partner',
        'odoo14-addon-membership_extension',
        'odoo14-addon-membership_withdrawal',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
