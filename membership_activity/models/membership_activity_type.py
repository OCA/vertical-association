from odoo import fields, models


class MembershipActivityType(models.Model):
    _name = "membership.activity.type"
    _description = "Member Activity Type"
    _parent_store = True
    _parent_name = "parent_id"

    name = fields.Char()
    parent_id = fields.Many2one(
        comodel_name="membership.activity.type",
        string="Parent Activity Type",
        index=True,
    )
    child_ids = fields.One2many(
        comodel_name="membership.activity.type",
        inverse_name="parent_id",
        string="Sub Activity Types",
    )
    parent_path = fields.Char(index=True, unaccent=False)
