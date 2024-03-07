# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    dates_mandatory = fields.Boolean(related="membership_id.dates_mandatory")

    @api.constrains(
        "membership_id",
        "membership_type",
        "dates_mandatory",
        "date_from",
        "date_to",
    )
    def _check_mandatory_dates(self):
        lines = self.filtered(
            lambda line: line.membership_type != "custom" or line.dates_mandatory
        )
        return super(MembershipLine, lines)._check_mandatory_dates()
