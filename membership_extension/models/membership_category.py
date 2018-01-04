# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MembershipCategory(models.Model):
    _name = "membership.membership_category"
    _description = "Membership category"

    name = fields.Char(required=True, translate=True)
