# Copyright 2019 Yu Weng <yweng@elegosoft.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def create_membership_invoice(self, product_id=None, datas=None):
        product_id = product_id or datas.get('membership_product_id')
        amount = datas.get('amount', 0.0)
        product = self.env['product.product'].browse(product_id)
        invoice_list = []
        if product.membership_set:
            for partner in self:
                if partner.free_member:
                    raise UserError(_("Partner is a free Member."))
                account_id = partner.property_account_receivable_id.id
                w = _("Partner doesn't have an account to make the invoice.")
                if not account_id:
                    raise UserError(w)
                position_id = partner.property_account_position_id.id
                invoice = self.env['account.invoice'].create({
                    'partner_id': partner.id,
                    'account_id': account_id,
                    'fiscal_position_id': position_id
                })
                for p in product.membership_set_products:
                    price_dict = p.price_compute('list_price')
                    amount = price_dict.get(p.id) or 0
                    line_values = {
                        'product_id': p.id,
                        'price_unit': amount,
                        'invoice_id': invoice.id,
                    }

                    # create a record in cache, apply onchange
                    # then revert back to a dictionnary
                    invoice_line = self.env['account.invoice.line']\
                        .new(line_values)
                    invoice_line._onchange_product_id()
                    line_values = invoice_line._convert_to_write({
                        name: invoice_line[name]
                        for name in invoice_line._cache
                    })
                    line_values['price_unit'] = amount
                    invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
                invoice_list.append(invoice.id)
                invoice.compute_taxes()
        else:
            invoice_list = super(ResPartner, self).create_membership_invoice(
                product_id=product_id,
                datas=datas
            )
        return invoice_list
