# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MembershipCategory(models.Model):
    _name = "membership.membership_category"
    _description = "Membership category"

    name = fields.Char(required=True, translate=True)
