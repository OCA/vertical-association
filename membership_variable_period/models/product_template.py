# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def _get_next_date(self, date):
        """Get the date that results on incrementing given date an interval of
        time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date incremented in 'interval' units of 'unit'.
        """
        self.ensure_one()
        if isinstance(date, str):
            date = fields.Date.from_string(date)
        if self.membership_interval_unit == 'days':
            return date + timedelta(days=self.membership_interval_qty)
        elif self.membership_interval_unit == 'weeks':
            return date + timedelta(weeks=self.membership_interval_qty)
        elif self.membership_interval_unit == 'months':
            return date + relativedelta(months=self.membership_interval_qty)
        elif self.membership_interval_unit == 'years':
            return date + relativedelta(years=self.membership_interval_qty)

    membership_type = fields.Selection(
        selection=[('fixed', 'Fixed dates'),
                   ('variable', 'Variable periods')],
        default='fixed', string="Membership type", required=True)
    membership_interval_qty = fields.Integer(
        string="Interval quantity", default=1)
    membership_interval_unit = fields.Selection(
        selection=[('days', 'days'),
                   ('weeks', 'weeks'),
                   ('months', 'months'),
                   ('years', 'years')],
        string="Interval unit", default='years')

    def _correct_vals_membership_type(self, vals, membership_type):
        if membership_type == 'variable':
            vals['membership_date_from'] = False
            vals['membership_date_to'] = False
        return vals

    @api.model
    def create(self, vals):
        self._correct_vals_membership_type(
            vals, vals.get('membership_type', 'fixed'))
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        self._correct_vals_membership_type(
            vals, vals.get('membership_type', self.membership_type))
        return super(ProductTemplate, self).write(vals)
