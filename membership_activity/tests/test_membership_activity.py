# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestMembershipActivity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Member"})
        self.project = self.env["project.project"].create({"name": "Test project"})
        self.membership_activity_type = self.env["membership.activity.type"].create(
            {"name": "Testing"}
        )
        self.membership_activity = self.env["membership.activity"].create(
            {
                "partner_id": self.partner.id,
                "project_id": self.project.id,
                "date": fields.Date.today(),
                "type_id": self.membership_activity_type.id,
            }
        )

    def test_name_get(self):
        # This test is added to increase coverage
        self.assertTrue(self.membership_activity.name_get())

    def test_reconcile_partner(self):
        # This test is added to increase coverage
        self.membership_activity.partner_id = False
        self.membership_activity.reconcile_partner()

    def test_get_last_membership_activity_date_by_type(self):
        membership_activity = self.project.get_last_membership_activity_date_by_type(
            False
        )
        self.assertEqual(membership_activity, datetime.min)
        membership_activity = self.project.get_last_membership_activity_date_by_type(
            self.membership_activity_type.id
        )
        self.assertEqual(membership_activity, self.membership_activity.date)

    def test_open_membership_activity(self):
        action = self.partner.open_membership_activity()
        self.assertEqual(action["domain"], [("partner_id", "in", self.partner.ids)])
