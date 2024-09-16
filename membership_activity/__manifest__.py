{
    "name": "Membership Activity",
    "summary": "Track activity of members",
    "category": "Membership",
    "version": "16.0.1.0.0",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "license": "AGPL-3",
    "depends": ["membership", "project"],
    "data": [
        "data/reconcile_partner_cron.xml",
        "security/ir_model_access.xml",
        "views/res_partner_view.xml",
        "views/membership_activity_view.xml",
        "views/membership_activity_type_view.xml",
        "menuitems.xml",
    ],
}
