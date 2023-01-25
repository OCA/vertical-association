from odoo import fields, models


class MembershipSectionMembership(models.Model):
    _name = "membership.section.membership"
    _description = "Section Membership"

    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")
    section_id = fields.Many2one(
        "membership.section", required=True, ondelete="cascade"
    )
    start_date = fields.Date(default=fields.Date.today)
