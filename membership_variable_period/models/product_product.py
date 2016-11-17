# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_next_date(self, date, qty=1):
        self.ensure_one()
        return self.product_tmpl_id._get_next_date(date, qty=qty)
