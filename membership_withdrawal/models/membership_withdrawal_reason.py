# Copyright 2016 Tecnativa  - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MembershipWithdrawalReason(models.Model):
    _name = "membership.withdrawal_reason"
    _description = "Reason for withdrawal in membership"

    name = fields.Char(required=True, translate=True)
