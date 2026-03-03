# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, timedelta

from odoo import api, models


class Partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _cron_membership_expiry_mail(self):
        expiry_date = date.today() + timedelta(days=30)
        expiring_members = self.search(
            [
                ("membership_stop", "=", expiry_date),
                ("membership_state", "=", "paid"),
            ]
        )
        for member in expiring_members:
            template = self.env.ref(
                "membership_expiry_mail.mail_template_membership_expiry"
            )
            template.send_mail(member.id)
