# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta

MEMBERSHIP_TYPE = [('fixed', 'Fixed dates'), ('variable', 'Variable periods')]
INTERVAL_UNIT = [('days', 'days'), ('weeks', 'weeks'), 
                 ('months', 'months'), ('years', 'years')]

class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_type = fields.Selection(selection=MEMBERSHIP_TYPE,
                                       string="Membership type",
                                       default='fixed', required=True)
    membership_interval_qty = fields.Integer(string="Interval quantity", 
                                             default=1)
    membership_interval_unit = fields.Selection(selection=INTERVAL_UNIT,
                                                string="Interval unit", 
                                                default='years')

    @api.model
    def create(self, vals):
        if vals.get('membership_type'):
            vals.update(self._correct_vals_membership_type(vals))
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('membership_type'):
            vals.update(self._correct_vals_membership_type(vals))
        return super(ProductTemplate, self).write(vals)

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
        else: return date

    @api.multi
    def _correct_vals_membership_type(self, vals):
        if vals.get('membership_type') == 'variable':
            return {'membership_date_from': False, 'membership_date_to': False}
        return {}

