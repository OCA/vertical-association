# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MembershipDeclineReason(models.Model):
    _name = "membership.decline_reason"
    _description = "Reason for decline in membership"

    name = fields.Char(required=True, translate=True)
