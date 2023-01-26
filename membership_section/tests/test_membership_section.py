from odoo.tests import common


class TestMembership(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Section = cls.env["membership.section"]
        Partner = cls.env["res.partner"]
        Membership = cls.env["membership.section.membership"]

        cls.section_1 = Section.create({"name": "Test Section 1"})
        cls.section_2 = Section.create({"name": "Test Section 2"})
        cls.partner_1 = Partner.create({"name": "Test partner 1"})
        cls.partner_2 = Partner.create({"name": "Test partner 2"})

        cls.membership_1a = Membership.create(
            {
                "partner_id": cls.partner_1.id,
                "section_id": cls.section_1.id,
            }
        )
        cls.membership_1b = Membership.create(
            {
                "partner_id": cls.partner_2.id,
                "section_id": cls.section_1.id,
            }
        )
        cls.membership_2a = Membership.create(
            {
                "partner_id": cls.partner_1.id,
                "section_id": cls.section_2.id,
            }
        )

    def test_01_section_computed_fields(self):
        self.assertListEqual(
            self.section_1.partner_ids.ids, [self.partner_1.id, self.partner_2.id]
        )
        self.assertListEqual(self.section_2.partner_ids.ids, [self.partner_1.id])
        self.assertEqual(self.section_1.partner_ids_count, 2)
        self.assertEqual(self.section_2.partner_ids_count, 1)

    def test_02_partner_computed_fields(self):
        self.assertListEqual(
            self.partner_1.section_ids.ids, [self.section_1.id, self.section_2.id]
        )
        self.assertListEqual(self.partner_2.section_ids.ids, [self.section_1.id])
        self.assertEqual(self.partner_1.section_ids_count, 2)
        self.assertEqual(self.partner_2.section_ids_count, 1)

    def test_03_action_open_partner_view(self):
        res = self.section_1.action_open_partner_view()
        self.assertEqual(res["xml_id"], "membership.action_membership_members")
        self.assertEqual(
            res["domain"],
            "[('id','in',["
            + ",".join(map(str, self.section_1.partner_ids.ids))
            + "])]",
        )

        res = self.section_2.action_open_partner_view()
        self.assertEqual(
            res["views"], [(self.env.ref("base.view_partner_form").id, "form")]
        )
        self.assertEqual(res["res_id"], self.partner_1.id)

    def test_04_action_open_section_view(self):
        res = self.partner_1.action_open_section_view()
        self.assertEqual(res["xml_id"], "membership_section.membership_section_action")
        self.assertEqual(
            res["domain"],
            "[('id','in',["
            + ",".join(map(str, self.partner_1.section_ids.ids))
            + "])]",
        )

        res = self.partner_2.action_open_section_view()
        self.assertEqual(
            res["views"],
            [
                (
                    self.env.ref("membership_section.membership_section_view_form").id,
                    "form",
                )
            ],
        )
        self.assertEqual(res["res_id"], self.section_1.id)
