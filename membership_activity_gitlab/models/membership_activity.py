from odoo import api, fields, models


class MembershipActivity(models.Model):
    _inherit = "membership.activity"

    gitlab_email = fields.Char()
    gitlab_username = fields.Char()

    @api.depends("gitlab_email", "gitlab_username")
    def _compute_partner_id(self):
        result = super()._compute_partner_id()

        email_map = {}
        username_map = {}
        for activity in self.filtered(lambda a: a.gitlab_email or a.gitlab_username):
            if activity.gitlab_username:
                if activity.gitlab_username not in username_map:
                    username_map[activity.gitlab_username] = self.env[
                        "res.partner"
                    ].get_id_by_gitlab_username(activity.gitlab_username)
                activity.partner_id = username_map[activity.gitlab_username]
            elif activity.gitlab_email:
                if activity.gitlab_email not in email_map:
                    email_map[activity.gitlab_email] = self.env[
                        "res.partner"
                    ].get_id_by_gitlab_email(activity.gitlab_email)
                activity.partner_id = email_map[activity.gitlab_email]
        return result
