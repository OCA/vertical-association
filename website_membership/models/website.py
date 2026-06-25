# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def get_suggested_controllers(self):
        suggested_controllers = super().get_suggested_controllers()
        suggested_controllers.append(
            (
                self.env._("Members"),
                self.env["ir.http"]._url_for("/members"),
                "website_membership",
            )
        )
        return suggested_controllers
