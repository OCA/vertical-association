# Copyright 2024 Onestein (<http://www.onestein.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import date
from unittest.mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase

from odoo.addons.membership_prorate.models.account_move_line import AccountMoveLine


class TestMembershipProrate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Membership product with prorate",
                "membership": True,
                "membership_prorate": True,
                "membership_date_from": "2017-01-01",
                "membership_date_to": "2017-12-31",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test",
            }
        )

    def create_membership_sale(self, date_order=False):
        vals = {
            "partner_id": self.partner.id,
            "date_order": date_order or fields.Date.today(),
            "order_line": [
                (
                    0,
                    None,
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 1,
                    },
                )
            ],
        }
        return self.env["sale.order"].create(vals)

    def test_create_sale_membership_product_wo_prorate(self):
        self.product.membership_prorate = False
        sale = self.create_membership_sale()
        self.assertEqual(sale.order_line[0].product_uom_qty, 1.0)

    def test_create_sale_membership_product_prorate(self):
        sale = self.create_membership_sale(date_order=date(2017, 7, 1))
        self.assertAlmostEqual(sale.order_line[0].product_uom_qty, 0.50, 2)
        sale = self.create_membership_sale(date_order=date(2016, 7, 1))
        self.assertAlmostEqual(sale.order_line[0].product_uom_qty, 1.0, 2)
        sale = self.create_membership_sale(date_order=date(2018, 7, 1))
        self.assertAlmostEqual(sale.order_line[0].product_uom_qty, 0, 2)

    def test_create_sale_membership_prorate_variable_period(self):
        """It is a test for case where membership type is set to variable
        on product with membership_prorate_variable_period not installed"""

        def _get_membership_interval(self, product, date):
            return False, False

        with patch.object(
            AccountMoveLine,
            "_get_membership_interval",
            _get_membership_interval,
        ):
            sale = self.create_membership_sale(date_order=date(2017, 7, 1))
            self.assertEqual(sale.order_line[0].product_uom_qty, 1.0)
