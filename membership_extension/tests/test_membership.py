# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from psycopg2 import IntegrityError

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import common
from odoo.tools import mute_logger


class TestMembership(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        date_today = fields.Date.today()
        cls.account_bank_type = cls.env["account.account.type"].create(
            {
                "name": "Test bank account type",
                "type": "liquidity",
                "internal_group": "asset",
            }
        )
        cls.account_bank = cls.env["account.account"].create(
            {
                "name": "Test bank account",
                "code": "BANK",
                "user_type_id": cls.account_bank_type.id,
                "reconcile": True,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test journal",
                "code": "TEST",
                "type": "sale",
                "default_account_id": cls.account_bank.id,
            }
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Test bank journal", "code": "TB", "type": "bank"}
        )
        cls.account_partner_type = cls.env["account.account.type"].create(
            {
                "name": "Test partner account type",
                "type": "receivable",
                "internal_group": "asset",
            }
        )
        cls.account_partner = cls.env["account.account"].create(
            {
                "name": "Test partner account",
                "code": "PARTNER",
                "user_type_id": cls.account_partner_type.id,
                "reconcile": True,
            }
        )
        cls.account_product_type = cls.env["account.account.type"].create(
            {
                "name": "Test product account type",
                "type": "other",
                "internal_group": "asset",
            }
        )
        cls.account_product = cls.env["account.account"].create(
            {
                "name": "Test product account",
                "code": "PRODUCT",
                "user_type_id": cls.account_product_type.id,
            }
        )
        cls.next_two_months = date_today + timedelta(days=60)
        cls.next_month = date_today + timedelta(days=30)
        cls.yesterday = date_today - timedelta(days=1)
        cls.category_gold = cls.env.ref("membership_extension.membership_category_gold")
        cls.category_silver = cls.env.ref(
            "membership_extension.membership_category_silver"
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "property_account_receivable_id": cls.account_partner.id,
            }
        )
        cls.child = cls.env["res.partner"].create(
            {"name": "Test child", "associate_member": cls.partner.id}
        )
        cls.gold_product = cls.env["product.product"].create(
            {
                "type": "service",
                "name": "Membership Gold",
                "membership": True,
                "membership_date_from": fields.Date.today(),
                "membership_date_to": cls.next_month,
                "membership_category_id": cls.category_gold.id,
                "list_price": 100.00,
            }
        )
        cls.silver_product = cls.env["product.product"].create(
            {
                "type": "service",
                "name": "Membership Silver",
                "membership": True,
                "membership_date_from": fields.Date.today(),
                "membership_date_to": cls.next_two_months,
                "membership_category_id": cls.category_silver.id,
                "list_price": 50.00,
            }
        )
        cls.current_year = date_today.year

    def test_compute_membership(self):
        line = self.env["membership.membership_line"].create(
            {
                "membership_id": self.gold_product.id,
                "member_price": 100.00,
                "date": fields.Date.today(),
                "date_from": fields.Date.today(),
                "date_to": self.next_month,
                "partner": self.partner.id,
                "state": "waiting",
            }
        )
        self.assertEqual("waiting", self.partner.membership_state)
        self.assertFalse(self.partner.membership_start)
        self.assertFalse(self.partner.membership_last_start)
        self.assertFalse(self.partner.membership_stop)
        self.assertFalse(self.partner.membership_cancel)
        self.assertEqual("waiting", self.child.membership_state)
        self.assertFalse(self.child.membership_start)
        self.assertFalse(self.child.membership_last_start)
        self.assertFalse(self.child.membership_stop)
        self.assertFalse(self.child.membership_cancel)
        line.write({"state": "invoiced"})
        self.assertEqual("invoiced", self.partner.membership_state)
        self.assertEqual(fields.Date.today(), self.partner.membership_start)
        self.assertEqual(fields.Date.today(), self.partner.membership_last_start)
        self.assertEqual(self.next_month, self.partner.membership_stop)
        self.assertFalse(self.partner.membership_cancel)
        self.assertEqual("invoiced", self.child.membership_state)
        self.assertEqual(fields.Date.today(), self.child.membership_start)
        self.assertEqual(fields.Date.today(), self.child.membership_last_start)
        self.assertEqual(self.next_month, self.child.membership_stop)
        self.assertFalse(self.child.membership_cancel)
        line.write({"date_cancel": self.yesterday})
        self.assertEqual("old", self.partner.membership_state)
        self.assertEqual(fields.Date.today(), self.partner.membership_start)
        self.assertEqual(fields.Date.today(), self.partner.membership_last_start)
        self.assertEqual(self.yesterday, self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual("old", self.child.membership_state)
        self.assertEqual(fields.Date.today(), self.child.membership_start)
        self.assertEqual(fields.Date.today(), self.child.membership_last_start)
        self.assertEqual(self.yesterday, self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        line.write({"state": "canceled"})
        self.assertEqual("none", self.partner.membership_state)
        self.assertFalse(self.partner.membership_start)
        self.assertFalse(self.partner.membership_last_start)
        self.assertFalse(self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual("none", self.child.membership_state)
        self.assertFalse(self.child.membership_start)
        self.assertFalse(self.child.membership_last_start)
        self.assertFalse(self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        other_line = self.env["membership.membership_line"].create(
            {
                "membership_id": self.silver_product.id,
                "member_price": 100.00,
                "date": fields.Date.today(),
                "date_from": fields.Date.today(),
                "date_to": self.next_two_months,
                "partner": self.partner.id,
                "state": "waiting",
            }
        )
        self.assertEqual("waiting", self.partner.membership_state)
        self.assertFalse(self.partner.membership_start)
        self.assertFalse(self.partner.membership_last_start)
        self.assertFalse(self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual("waiting", self.child.membership_state)
        self.assertFalse(self.child.membership_start)
        self.assertFalse(self.child.membership_last_start)
        self.assertFalse(self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        other_line.write({"state": "paid"})
        self.assertEqual("paid", self.partner.membership_state)
        self.assertEqual(fields.Date.today(), self.partner.membership_start)
        self.assertEqual(fields.Date.today(), self.partner.membership_last_start)
        self.assertEqual(self.next_two_months, self.partner.membership_stop)
        self.assertEqual(self.yesterday, self.partner.membership_cancel)
        self.assertEqual("paid", self.child.membership_state)
        self.assertEqual(fields.Date.today(), self.child.membership_start)
        self.assertEqual(fields.Date.today(), self.child.membership_last_start)
        self.assertEqual(self.next_two_months, self.child.membership_stop)
        self.assertEqual(self.yesterday, self.child.membership_cancel)
        self.partner.free_member = True
        self.assertEqual("free", self.child.membership_state)

    def test_category(self):
        line_one = self.env["membership.membership_line"].create(
            {
                "membership_id": self.gold_product.id,
                "member_price": 100.00,
                "date": fields.Date.today(),
                "date_from": fields.Date.today(),
                "date_to": self.next_month,
                "partner": self.partner.id,
                "state": "invoiced",
            }
        )
        self.assertEqual(self.category_gold, self.partner.membership_category_ids)
        self.assertEqual("Gold", self.partner.membership_categories)
        self.assertEqual(self.category_gold, self.child.membership_category_ids)
        self.assertEqual("Gold", self.child.membership_categories)
        line_two = self.env["membership.membership_line"].create(
            {
                "membership_id": self.silver_product.id,
                "member_price": 50.00,
                "date": fields.Date.today(),
                "date_from": fields.Date.today(),
                "date_to": self.next_two_months,
                "partner": self.partner.id,
                "state": "paid",
            }
        )
        self.assertEqual(
            self.category_gold + self.category_silver,
            self.partner.membership_category_ids,
        )
        self.assertTrue("Silver" in self.partner.membership_categories)
        self.assertTrue("Gold" in self.partner.membership_categories)
        self.assertEqual(
            self.category_gold + self.category_silver,
            self.child.membership_category_ids,
        )
        self.assertTrue("Silver" in self.child.membership_categories)
        self.assertTrue("Gold" in self.child.membership_categories)
        line_one.write({"state": "canceled"})
        self.assertEqual(self.category_silver, self.partner.membership_category_ids)
        self.assertEqual("Silver", self.partner.membership_categories)
        self.assertEqual(self.category_silver, self.child.membership_category_ids)
        self.assertEqual("Silver", self.child.membership_categories)
        line_two.write({"state": "waiting"})
        self.assertFalse(self.partner.membership_category_ids.ids)
        self.assertFalse(self.partner.membership_categories)
        self.assertFalse(self.child.membership_category_ids.ids)
        self.assertFalse(self.child.membership_categories)

    def test_remove_membership_line_with_invoice(self):
        invoice_form = common.Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.invoice_date = fields.Date.today()
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as invoice_line_form:
            invoice_line_form.name = self.gold_product.name
            invoice_line_form.product_id = self.gold_product
            invoice_line_form.price_unit = 100.0
        invoice = invoice_form.save()

        with self.assertRaises(UserError):
            self.partner.member_lines[0].unlink()
        invoice.invoice_line_ids.with_context(check_move_validity=False).unlink()
        self.assertFalse(self.partner.member_lines)

    def test_membership_line_onchange(self):
        line = self.env["membership.membership_line"].create(
            {
                "membership_id": self.gold_product.id,
                "member_price": 100.00,
                "date": fields.Date.today(),
                "partner": self.partner.id,
                "state": "invoiced",
            }
        )
        line._onchange_membership_date()
        self.assertEqual(100.00, line.member_price)
        self.assertEqual(fields.Date.today(), line.date_from)
        self.assertEqual(self.next_month, line.date_to)
        line.write({"membership_id": self.silver_product.id})
        line._onchange_membership_date()
        self.assertEqual(50, line.member_price)
        self.assertEqual(fields.Date.today(), line.date_from)
        self.assertEqual(self.next_two_months, line.date_to)

    def test_invoice(self):
        invoice_form = common.Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.invoice_date = fields.Date.today()
        invoice_form.partner_id = self.partner
        with invoice_form.invoice_line_ids.new() as invoice_line_form:
            invoice_line_form.name = self.gold_product.name
            invoice_line_form.product_id = self.gold_product
            invoice_line_form.price_unit = 100.0
            invoice_line_form.quantity = 1.0
        invoice = invoice_form.save()

        line = self.partner.member_lines[0]
        self.assertEqual("waiting", line.state)
        self.assertEqual(fields.Date.today(), line.date_from)
        self.assertEqual(self.next_month, line.date_to)
        invoice.action_post()  # validate invoice
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(line.state, "invoiced")

        # pay invoice
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create(
            {
                "amount": invoice.amount_total,
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )._create_payments()

        self.assertEqual("paid", invoice.payment_state)
        self.assertEqual("paid", line.state)
        self.env["account.payment"].search(
            [("partner_id", "=", self.partner.id)]
        ).action_cancel()
        invoice.button_cancel()
        self.assertEqual("canceled", line.state)
        invoice.button_draft()
        self.assertEqual("waiting", line.state)
        invoice.state = "draft"  # HACK: Odoo resets this to open
        invoice.action_post()  # validate invoice
        self.assertEqual("invoiced", line.state)

        # pay invoice
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create(
            {
                "amount": invoice.amount_total,
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )._create_payments()
        self.assertEqual("paid", line.state)

        # refund invoice
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "refund_method": "cancel",
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertEqual("canceled", line.state)
        refund.button_cancel()
        self.assertEqual("paid", line.state)
        refund.button_draft()
        self.assertEqual("invoiced", line.state)

        invoice.button_draft()
        invoice_form = common.Form(invoice)
        with invoice_form.invoice_line_ids.edit(0) as invoice_line_form:
            invoice_line_form.quantity = 0.5
        invoice = invoice_form.save()
        self.assertNotEqual(invoice.amount_untaxed, refund.amount_untaxed)
        invoice.action_post()
        self.assertEqual("invoiced", line.state)

    def test_check_membership_all(self):
        self.env["membership.membership_line"].create(
            {
                "membership_id": self.gold_product.id,
                "member_price": 100.00,
                "date": fields.Date.today(),
                "date_from": fields.Date.today(),
                "date_to": self.next_month,
                "partner": self.partner.id,
                "state": "waiting",
            }
        )
        # Force another state to check if the recomputation is done
        self.partner.membership_state = "none"
        self.env["res.partner"].check_membership_all()
        self.assertEqual(self.partner.membership_state, "waiting")

    def test_check_membership_expiry(self):
        self.env["membership.membership_line"].create(
            {
                "membership_id": self.gold_product.id,
                "member_price": 100.00,
                "date": self.yesterday,
                "date_from": self.yesterday,
                "date_to": self.yesterday,
                "partner": self.partner.id,
                "state": "waiting",
            }
        )
        self.env["res.partner"]._cron_update_membership()
        self.assertEqual(self.partner.membership_state, "none")

    @mute_logger("odoo.sql_db")
    def test_unlink(self):
        self.env["membership.membership_line"].create(
            {
                "membership_id": self.gold_product.id,
                "member_price": 0,
                "partner": self.partner.id,
            }
        )
        # We can't delete a partner with member lines
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.partner.unlink()
        # Create a brand new partner and delete it
        partner2 = self.env["res.partner"].create({"name": "no member"})
        partner2.unlink()
        self.assertFalse(partner2.exists())

    def test_adhered_member(self):
        self.env["membership.membership_line"].create(
            {
                "membership_id": self.gold_product.id,
                "member_price": 100.00,
                "date": fields.Date.today(),
                "date_from": fields.Date.today(),
                "date_to": self.next_month,
                "partner": self.partner.id,
                "state": "waiting",
            }
        )
        self.child.is_adhered_member = True
        self.child.membership_start_adhered = "2018-01-26"
        self.assertEqual(self.child.membership_start, datetime(2018, 1, 26).date())
        self.child.associate_member = False
        self.assertFalse(self.child.is_adhered_member)

    def test_category_multicompany(self):
        company_a = self.env["res.company"].create({"name": "Test company A"})
        company_b = self.env["res.company"].create({"name": "Test company B"})

        # set all the product templates for Gold Membership to Company B
        templates = self.env["product.template"].search(
            [("membership_category_id", "in", self.category_gold.ids)]
        )
        for template in templates:
            template.company_id = company_b

        # Gold Membership Category cannot be assigned to Company A
        for template in templates:
            template.membership_category_id = self.category_gold
            self.assertNotEqual(template.membership_category_id.company_id, company_a)
        with self.assertRaises(ValidationError):
            self.category_gold.company_id = company_a

        # force Gold Membership Category assignment to Company A
        self.category_gold.with_context(
            bypass_company_validation=True
        ).company_id = company_a

        # Company can be removed from any Membership Category
        self.category_gold.company_id = False

        # set all the product templates for Gold Membership to Company A
        templates = self.env["product.template"].search(
            [("membership_category_id", "in", self.category_gold.ids)]
        )
        for template in templates:
            self.assertTrue(template.membership_category_id)
            template.company_id = company_a

        # Gold Membership Category can now be assigned to Company A
        self.category_gold.company_id = company_a

        # test onchange
        for template in templates:
            self.assertTrue(template.membership_category_id)
            template.company_id = company_b
            self.assertFalse(template.membership_category_id)
