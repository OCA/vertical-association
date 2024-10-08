from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_id_by_gitlab_email(self, gitlab_email):
        return self.search(
            [
                "|",
                ("gitlab_email", "=ilike", gitlab_email),
                ("email", "=ilike", gitlab_email),
            ],
            limit=1,
        ).id

    @api.model
    def get_id_by_gitlab_username(self, gitlab_username):
        return self.search([("gitlab_username", "=ilike", gitlab_username)], limit=1).id
