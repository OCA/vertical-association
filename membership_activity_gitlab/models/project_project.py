from datetime import datetime, timezone

import dateutil

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    gitlab_id = fields.Many2one(comodel_name="gitlab", string="Gitlab Connection")

    gitlab_full_name = fields.Char(
        string="Gitlab Fullname",
        help="Namespace + project name e.g. 'gitlab-org/gitlab' (for https://gitlab.com/gitlab-org/gitlab)",
    )

    @api.model
    def _gitlab_datetime_to_odoo(self, datetime_string):
        dt = dateutil.parser.parse(datetime_string)
        dt = dt.astimezone(timezone.utc)
        dt = dt.replace(tzinfo=None)
        return dt

    def get_gitlab_commits(self):
        until = fields.Datetime.now()
        for project in self:
            since = project.get_last_membership_activity_date_by_type(
                "membership_activity_cde.commit"
            )
            # Because pagination excludes X-Total header if it returns more than 10000 records we do it this way
            # https://docs.gitlab.com/ee/user/gitlab_com/index.html#pagination-response-headers
            project.with_delay(max_retries=0).get_gitlab_commits_iterated(
                1, project.gitlab_id.per_page, since, until
            )

    def get_gitlab_commits_iterated(self, page, per_page, since, until):
        self.ensure_one()
        gl = self.gitlab_id.get_server_connection()
        project = gl.projects.get(self.gitlab_full_name)
        params = {
            "page": page,
            "per_page": per_page,
            "until": fields.Datetime.to_string(until),
        }
        if since > datetime.min:
            params.update(since=fields.Datetime.to_string(since))
        commits = project.commits.list(**params)
        activity_type = self.env.ref("membership_activity_cde.commit")
        vals_list = []
        for commit in commits:
            vals_list.append(
                {
                    "project_id": self.id,
                    "gitlab_email": commit.author_email,
                    "type_id": activity_type.id,
                    "url": commit.web_url,
                    "date": self._gitlab_datetime_to_odoo(commit.authored_date),
                }
            )
        self.env["membership.activity"].create(vals_list)
        if commits:
            self.with_delay(max_retries=0).get_gitlab_commits_iterated(
                page + 1, per_page, since, until
            )

    def get_gitlab_merge_requests(self):
        until = fields.Datetime.now()
        for project in self:
            since = project.get_last_membership_activity_date_by_type(
                "membership_activity_cde.pr"
            )
            # Because pagination excludes X-Total header if it returns more than 10000 records we do it this way
            # https://docs.gitlab.com/ee/user/gitlab_com/index.html#pagination-response-headers
            project.with_delay(max_retries=0).get_gitlab_merge_requests_iterated(
                1, project.gitlab_id.per_page, since, until
            )

    def get_gitlab_merge_requests_iterated(self, page, per_page, since, until):
        self.ensure_one()
        gl = self.gitlab_id.get_server_connection()
        project = gl.projects.get(self.gitlab_full_name)
        params = {
            "page": page,
            "per_page": per_page,
            "created_before": fields.Datetime.to_string(until),
        }
        if since > datetime.min:
            params.update(created_after=fields.Datetime.to_string(since))
        merge_requests = project.mergerequests.list(**params)
        activity_type = self.env.ref("membership_activity_cde.pr")
        vals_list = []
        for merge_request in merge_requests:
            vals_list.append(
                {
                    "project_id": self.id,
                    "gitlab_username": merge_request.author["username"],
                    "type_id": activity_type.id,
                    "url": merge_request.web_url,
                    "date": self._gitlab_datetime_to_odoo(merge_request.created_at),
                }
            )
        self.env["membership.activity"].create(vals_list)
        if merge_requests:
            self.with_delay(max_retries=0).get_gitlab_merge_requests_iterated(
                page + 1, per_page, since, until
            )

    def get_gitlab_issues(self):
        until = fields.Datetime.now()
        for project in self:
            since = project.get_last_membership_activity_date_by_type(
                "membership_activity_cde.issue"
            )
            # Because pagination excludes X-Total header if it returns more than 10000 records we do it this way
            # https://docs.gitlab.com/ee/user/gitlab_com/index.html#pagination-response-headers
            project.with_delay(max_retries=0).get_gitlab_issues_iterated(
                1, project.gitlab_id.per_page, since, until
            )

    def get_gitlab_issues_iterated(self, page, per_page, since, until):
        self.ensure_one()
        gl = self.gitlab_id.get_server_connection()
        project = gl.projects.get(self.gitlab_full_name)
        params = {
            "page": page,
            "per_page": per_page,
            "created_before": fields.Datetime.to_string(until),
        }
        if since > datetime.min:
            params.update(created_after=fields.Datetime.to_string(since))
        issues = project.issues.list(**params)
        activity_type = self.env.ref("membership_activity_cde.issue")
        vals_list = []
        for issue in issues:
            vals_list.append(
                {
                    "project_id": self.id,
                    "gitlab_username": issue.author["username"],
                    "type_id": activity_type.id,
                    "url": issue.web_url,
                    "date": self._gitlab_datetime_to_odoo(issue.created_at),
                }
            )
        self.env["membership.activity"].create(vals_list)
        if issues:  # Sometimes it returns 99 records somehow
            self.with_delay(max_retries=0).get_gitlab_issues_iterated(
                page + 1, per_page, since, until
            )

    def get_gitlab_notes(self):
        until = fields.Datetime.now()
        for project in self:
            since = project.get_last_membership_activity_date_by_type(
                "membership_activity_cde.comment"
            )
            # Because pagination excludes X-Total header if it returns more than 10000 records we do it this way
            # https://docs.gitlab.com/ee/user/gitlab_com/index.html#pagination-response-headers
            project.with_delay(max_retries=0).get_gitlab_notes_iterated(
                1, project.gitlab_id.per_page, since, until
            )

    def get_gitlab_notes_iterated(self, page, per_page, since, until):
        self.ensure_one()
        gl = self.gitlab_id.get_server_connection()
        project = gl.projects.get(self.gitlab_full_name)
        params = {
            "page": page,
            "per_page": per_page,
            "before": fields.Datetime.to_string(until),
            "target_type": "note",
        }
        if since > datetime.min:
            params.update(after=fields.Datetime.to_string(since))
        events = project.events.list(**params)
        activity_type = self.env.ref("membership_activity_cde.comment")
        vals_list = []
        for event in events:
            note = event.note
            if note["system"]:  # Exclude system messages
                continue
            vals_list.append(
                {
                    "project_id": self.id,
                    "gitlab_username": note["author"]["username"],
                    "type_id": activity_type.id,
                    "url": note["author"]["web_url"],  # No web_url on comments
                    "date": self._gitlab_datetime_to_odoo(note["created_at"]),
                }
            )
        self.env["membership.activity"].create(vals_list)
        if events:  # Sometimes it returns 99 records somehow
            self.with_delay(max_retries=0).get_gitlab_notes_iterated(
                page + 1, per_page, since, until
            )

    def get_gitlab_approvals(self):
        until = fields.Datetime.now()
        for project in self:
            since = project.get_last_membership_activity_date_by_type(
                "membership_activity_cde.review"
            )
            # Because pagination excludes X-Total header if it returns more than 10000 records we do it this way
            # https://docs.gitlab.com/ee/user/gitlab_com/index.html#pagination-response-headers
            project.with_delay(max_retries=0).get_gitlab_approvals_iterated(
                1, project.gitlab_id.per_page, since, until
            )

    def get_gitlab_approvals_iterated(self, page, per_page, since, until):
        self.ensure_one()
        gl = self.gitlab_id.get_server_connection()
        project = gl.projects.get(self.gitlab_full_name)
        params = {
            "page": page,
            "per_page": per_page,
            "before": fields.Datetime.to_string(until),
            "action": "approved",
        }
        if since > datetime.min:
            params.update(after=fields.Datetime.to_string(since))
        events = project.events.list(**params)
        activity_type = self.env.ref("membership_activity_cde.review")
        vals_list = []
        for event in events:
            vals_list.append(
                {
                    "project_id": self.id,
                    "gitlab_username": event.author_username,
                    "type_id": activity_type.id,
                    "url": event.author["web_url"],  # No web_url so use authors web_url
                    "date": self._gitlab_datetime_to_odoo(event.created_at),
                }
            )
        self.env["membership.activity"].create(vals_list)
        if events:  # Sometimes it returns 99 records somehow
            self.with_delay(max_retries=0).get_gitlab_approvals_iterated(
                page + 1, per_page, since, until
            )

    @api.model
    def cron_import_gitlab_activity(self):
        projects = self.search(
            [("gitlab_full_name", "!=", False), ("gitlab_id", "!=", False)]
        )
        projects.get_gitlab_commits()
        projects.get_gitlab_merge_requests()
        projects.get_gitlab_issues()
        projects.get_gitlab_notes()
        projects.get_gitlab_approvals()
