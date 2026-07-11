# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestMembershipInitialFee(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        # AccountTestInvoicingCommon installs a generic chart of accounts:
        # invoice creation needs a sale journal and default accounts, which
        # a bare test database no longer provides in Odoo 19.
        super().setUpClass()
        cls.product_category = cls.env["product.category"].create({"name": "test_cat"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 100}
        )
        cls.product_fee = cls.env["product.product"].create(
            {
                "name": "Membership Fee",
                "list_price": 1.0,
                "type": "service",
                "categ_id": cls.product_category.id,
            }
        )
        cls.product_fixed = cls.env["product.product"].create(
            {
                "name": "Membership product with fixed initial fee",
                "membership": True,
                "initial_fee": "fixed",
                "product_fee": cls.product_fee.id,
                "fixed_fee": 50.0,
                "list_price": 150.0,
                "type": "service",
                "categ_id": cls.product_category.id,
                "membership_date_from": "2017-01-01",
                "membership_date_to": "2017-02-01",
            }
        )
        cls.product_percentage = cls.env["product.product"].create(
            {
                "name": "Membership product with percentage initial fee",
                "membership": True,
                "product_fee": cls.product_fee.id,
                "initial_fee": "percentage",
                "percentage_fee": 10.0,
                "list_price": 150.0,
                "type": "service",
                "categ_id": cls.product_category.id,
                "membership_date_from": "2017-01-01",
                "membership_date_to": "2017-02-01",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test"})

    def check_membership_invoice(self, invoice, expected_amount):
        self.assertEqual(
            len(invoice.invoice_line_ids), 2, "The created invoice should have 2 lines"
        )
        initial_fee_line = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_fee
        )
        self.assertEqual(
            initial_fee_line.price_unit,
            expected_amount,
            "The initial fee amount is not correct",
        )

    def test_create_invoice_wo_initial_fee(self):
        self.product_fixed.initial_fee = "none"
        invoice = self.partner.create_membership_invoice(self.product_fixed, 1.0)
        self.assertEqual(
            len(invoice.invoice_line_ids), 1, "The created invoice should have 1 lines"
        )

    def test_create_invoice_initial_fee_fixed(self):
        invoice = self.partner.with_context(
            check_move_validity=False
        ).create_membership_invoice(self.product_fixed, 1.0)
        self.check_membership_invoice(invoice, 50.0)

    def test_create_invoice_initial_fee_percentage(self):
        invoice = self.partner.with_context(
            check_move_validity=False
        ).create_membership_invoice(self.product_percentage, 150.0)
        self.check_membership_invoice(invoice, 15.0)

    def test_create_invoice_initial_fee_taxes(self):
        # In Odoo 19 account.tax requires an explicit tax group and
        # country when no localized chart of accounts is installed.
        country = self.env.company.country_id or self.env.ref("base.us")
        self.env.company.country_id = country
        tax_group = self.env["account.tax.group"].create(
            {"name": "Test Taxes", "country_id": country.id}
        )
        tax = self.env["account.tax"].create(
            {
                "name": "Tax",
                "amount_type": "percent",
                "amount": 0.10,
                "tax_group_id": tax_group.id,
                "country_id": country.id,
            }
        )
        self.product_fixed.product_fee.taxes_id = tax
        invoice = self.partner.with_context(
            check_move_validity=False
        ).create_membership_invoice(self.product_fixed, 150.0)
        initial_fee_line = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_fee
        )
        self.assertEqual(initial_fee_line.tax_ids, tax)

    def test_onchange_product_fee(self):
        membership_product = self.env["product.template"].new(
            {"name": "Test membership product"}
        )
        membership_product.product_fee = self.product
        self.assertEqual(membership_product.fixed_fee, self.product.list_price)
