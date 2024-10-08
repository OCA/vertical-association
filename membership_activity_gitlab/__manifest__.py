{
    "name": "Membership Gitlab Activity",
    "category": "Membership",
    "version": "16.0.1.0.0",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-association",
    "license": "AGPL-3",
    "depends": [
        "membership_activity",
        "membership_activity_cde",
        "partner_cde",
        "queue_job",
        "gitlab",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/project_view.xml",
        "menuitems.xml",
    ],
}
