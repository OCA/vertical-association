# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2019 Onestein - Andrea Stirpe
# Copyright 2023 Coop IT Easy SC
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_type = fields.Selection(
        selection=[("fixed", "Fixed dates")],
        default="fixed",
        required=True,
    )

    @api.model
    def _is_check_dates_for_type(self, membership_type):
        # Override this to pass more membership types to _check_membership_dates
        return membership_type == "fixed"

    @api.constrains(
        "membership_date_from",
        "membership_date_to",
        "membership",
        "membership_type",
    )
    def _check_membership_dates(self):
        return super(
            ProductTemplate,
            self.filtered(
                lambda record: self._is_check_dates_for_type(record.membership_type)
            ),
        )._check_membership_dates()

    @api.model
    def _correct_vals_membership_type(self, vals):
        """This method exists for downstream adopters to adjust some values
        prior to writing/creating a record. Typically this is used to set
        membership_date_from and membership_date_to to False.
        """
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._correct_vals_membership_type(vals)
        return super().create(vals_list)

    def write(self, vals):
        if not vals.get("membership_type"):
            return super().write(vals)
        for rec in self:
            rec._correct_vals_membership_type(vals)
            super(ProductTemplate, rec).write(vals)
        return True
