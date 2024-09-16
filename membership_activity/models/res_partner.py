from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_activity_ids = fields.One2many(
        comodel_name="membership.activity",
        inverse_name="partner_id",
        string="Member Activities",
    )
    membership_activity_count = fields.Integer(
        string="# of Activities",
        compute="_compute_membership_activity_count",
        store=True,
    )
    last_membership_activity_date = fields.Date(
        string="Last Activity Date",
        compute="_compute_last_membership_activity_date",
        store=True,
        copy=False,
    )

    @api.depends("membership_activity_ids")
    def _compute_membership_activity_count(self):
        for partner in self:
            partner.membership_activity_count = len(partner.membership_activity_ids)

    @api.depends("membership_activity_ids")
    def _compute_last_membership_activity_date(self):
        for partner in self:
            partner.last_membership_activity_date = (
                partner.membership_activity_ids
                and max(partner.membership_activity_ids.mapped("date"))
            )

    def open_membership_activity(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "membership_activity.membership_activity_action"
        )
        action["domain"] = [("partner_id", "in", self.ids)]
        return action
