# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership = fields.Boolean(help="Check if the product is eligible for membership.")
    membership_date_from = fields.Date(
        string="Membership Start Date",
        help="Date from which membership becomes active.",
    )
    membership_date_to = fields.Date(
        string="Membership End Date", help="Date until which membership remains active."
    )

    _membership_date_greater = models.Constraint(
        "check(membership_date_to >= membership_date_from)",
        "Error! Ending Date cannot be set before Beginning Date.",
    )
    membership_category_id = fields.Many2one(
        string="Membership category",
        comodel_name="membership.membership_category",
        compute="_compute_membership_category_id",
        readonly=False,
        store=True,
    )

    def _get_next_date(self, date, qty=1):
        self.ensure_one()
        if self.membership_date_to:
            date_to = fields.Date.from_string(self.membership_date_to)
            return date_to + timedelta(1)
        return False  # pragma: no cover

    @api.depends("company_id")
    def _compute_membership_category_id(self):
        """Reset the Membership Category in case a different Company is set"""
        for record in self:
            if record.company_id and record.membership_category_id.company_id:
                if record.membership_category_id.company_id != record.company_id:
                    record.membership_category_id = False

    @api.constrains("membership_date_from", "membership_date_to", "membership")
    def _check_membership_dates(self):
        if self.filtered(
            lambda record: record.membership
            and (not record.membership_date_from or not record.membership_date_to)
        ):
            raise ValidationError(
                self.env._(
                    "A membership product must have a start date and an end date."
                )
            )
