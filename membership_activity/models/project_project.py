from datetime import datetime

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    membership_activity_ids = fields.One2many(
        comodel_name="membership.activity",
        inverse_name="project_id",
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
        for project in self:
            project.membership_activity_count = len(project.membership_activity_ids)

    @api.depends("membership_activity_ids")
    def _compute_last_membership_activity_date(self):
        for project in self:
            project.last_membership_activity_date = (
                project.membership_activity_ids
                and max(project.membership_activity_ids.mapped("date"))
            )

    def get_last_membership_activity_date_by_type(self, type_id_or_xml_id):
        self.ensure_one()
        activity_type_id = type_id_or_xml_id
        if type(type_id_or_xml_id) == str:
            activity_type_id = self.env.ref(type_id_or_xml_id).id
        matching_activities = self.membership_activity_ids.filtered(
            lambda a: a.type_id.id == activity_type_id
        ).mapped("date")
        if not matching_activities:
            return datetime.min
        return max(matching_activities)
