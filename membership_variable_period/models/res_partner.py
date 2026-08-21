# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _membership_renewable_member_states(self):
        """Inherit this method to define renewable membership states.

        :return tuple: list of renewable membership states
        """
        return self._membership_member_states()

    def get_membership_renewal_date(self, product):
        """Retrieve the renewal date of a member for a given membership product.

        :param product (Model<product.product>): the affected product
        :return datetime.date: the renewal date of the member
        """
        self.ensure_one()
        last_date_to = False
        if (
            product
            and product.membership_type == "variable"
            and product.membership_category_id in self.membership_category_ids
        ):
            today = fields.Date.today()
            last_membership = self.member_lines.filtered(
                lambda line: line.category_id == product.membership_category_id
                and line.state in self._membership_renewable_member_states()
                and line.date_to
                and line.date_to >= today
                and (not line.date_cancel or line.date_cancel >= today)
            ).sorted("date_to", reverse=True)[:1]
            last_date_to = last_membership.date_to
        return last_date_to and last_date_to + timedelta(days=1)
