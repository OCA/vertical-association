# -*- coding: utf-8 -*-
# (c) 2015 Incaser Informatica S.L. - Sergio Teruel
# (c) 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestMembershipBoard(TransactionCase):
    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestMembershipBoard, self).setUp()
        self.board_tag = self.env.ref(
            'membership_board.'
            'membership_board_tag')
        self.position_president = self.env.ref(
            'membership_board.'
            'membership_board_position_president')
        self.position_secretary = self.env.ref(
            'membership_board.'
            'membership_board_position_secretary')

        # create membership partner
        self.member1 = self.env['res.partner'].create(
            {'name': 'Membership test (president)',
             'free_member': True,
             })
        self.member2 = self.env['res.partner'].create(
            {'name': 'Membership test (secretary)',
             'free_member': True,
             })
        self.member3 = self.env['res.partner'].create(
            {'name': 'Membership test (regular)',
             'free_member': True,
             })

        # create membership board
        self.board = self.env['membership.board'].create(
            {'name': 'Membership Board Test'})

        self.president = self.env['membership.board.member'].create(
            {'board_id': self.board.id,
             'position_id': self.position_president.id,
             'partner_id': self.member1.id,
             })
        self.secretary = self.env['membership.board.member'].create(
            {'board_id': self.board.id,
             'position_id': self.position_secretary.id,
             'partner_id': self.member2.id,
             })

        # Assign membership board active
        self.company = self.member1.company_id

    def test_board(self):
        self.assertNotIn(self.board_tag, self.member1.category_id)
        self.assertNotIn(self.board_tag, self.member2.category_id)
        self.assertNotIn(self.board_tag, self.member3.category_id)
        self.company.membership_board_id = self.board.id
        self.assertIn(self.board_tag, self.member1.category_id)
        self.assertIn(self.board_tag, self.member2.category_id)
        self.assertNotIn(self.board_tag, self.member3.category_id)
        self.assertEqual(self.board.president_id.id, self.member1.id)
        self.assertEqual(self.board.secretary_id.id, self.member2.id)

        # Delete tags
        self.member1.category_id = False
        self.member2.category_id = False
        self.member3.category_id = False

        # Recompute tags
        self.board.update_board_tag()
        self.assertIn(self.board_tag, self.member1.category_id)
        self.assertIn(self.board_tag, self.member2.category_id)
        self.assertNotIn(self.board_tag, self.member3.category_id)

        # Write in board
        self.board.write({'members_ids':
                          [(4, self.president.id, False),
                           (2, self.secretary.id, False)]})
        self.assertNotIn(self.board_tag, self.member2.category_id)

        # Delete active board from company
        self.company.membership_board_id = False
        self.assertNotIn(self.board_tag, self.member1.category_id)
        self.assertNotIn(self.board_tag, self.member2.category_id)
        self.assertNotIn(self.board_tag, self.member3.category_id)
