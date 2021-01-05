# Copyright 2016 Tecnativa  - Antonio Espinosa
# Copyright 2020 Tecnativa  - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MembershipWithdrawalReason(models.Model):
    _name = "membership.withdrawal_reason"
    _description = "Reason for withdrawal in membership"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, translate=True)
