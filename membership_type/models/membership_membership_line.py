# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    membership_type = fields.Selection(related="membership_id.membership_type")
