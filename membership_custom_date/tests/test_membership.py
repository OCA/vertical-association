# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestMembership(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "type": "service",
                "name": "Custom Membership",
                "membership": True,
                "membership_type": "custom",
                "list_price": 100,
                "dates_mandatory": True,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    def test_mandatory_dates(self):
        with self.assertRaises(ValidationError):
            self.env["membership.membership_line"].create(
                {
                    "membership_id": self.product.id,
                    "member_price": 100.00,
                    "date": fields.Date.today(),
                    # No dates
                    "partner": self.partner.id,
                    "state": "waiting",
                }
            )
        self.product.dates_mandatory = False
        self.env["membership.membership_line"].create(
            {
                "membership_id": self.product.id,
                "member_price": 100.00,
                "date": fields.Date.today(),
                # No dates
                "partner": self.partner.id,
                "state": "waiting",
            }
        )

    def test_check_membership_dates_required(self):
        invoice_form = Form(
            self.env["membership.invoice"].with_context(
                default_partner_id=self.partner.id
            )
        )
        invoice_form.product_id = self.product

        message = "is a required field"

        invoice_form.date_from = False
        invoice_form.date_to = False
        with self.assertRaisesRegex(AssertionError, message):
            invoice_form.save()

        invoice_form.date_from = "2023-01-01"
        invoice_form.date_to = False
        with self.assertRaisesRegex(AssertionError, message):
            invoice_form.save()

        invoice_form.date_from = False
        invoice_form.date_to = "2023-12-31"
        with self.assertRaisesRegex(AssertionError, message):
            invoice_form.save()

        invoice_form.date_from = "2023-01-01"
        invoice_form.date_to = "2023-12-31"
        invoice_form.save()

        self.product.dates_mandatory = False
        invoice_form.product_id = self.product
        invoice_form.date_from = False
        invoice_form.date_to = False
        invoice_form.save()

    def test_check_membership_invoice_check_dates(self):
        wizard = self.env["membership.invoice"].create(
            {
                "product_id": self.product.id,
                "member_price": 100,
            }
        )
        wizard = wizard.with_context(
            default_partner_id=self.partner.id,
            active_ids=self.partner.id,
        )

        self.assertEqual(wizard.product_id, self.product)

        message = "start and end dates are mandatory"

        # already the case, but to be explicit here
        wizard.date_from = False
        wizard.date_to = False
        with self.assertRaisesRegex(ValidationError, message):
            wizard.membership_invoice()

        wizard.date_from = "2023-01-01"
        wizard.date_to = False
        with self.assertRaisesRegex(ValidationError, message):
            wizard.membership_invoice()

        wizard.date_from = False
        wizard.date_to = "2023-12-31"
        with self.assertRaisesRegex(ValidationError, message):
            wizard.membership_invoice()

        wizard.date_from = "2023-01-01"
        wizard.date_to = "2023-12-31"
        wizard.membership_invoice()
