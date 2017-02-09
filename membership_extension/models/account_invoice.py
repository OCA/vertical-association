# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_cancel_draft(self):
        self.mapped('invoice_line').mapped('membership_lines').write({
            'date_cancel': False,
            'state': 'waiting',
        })
        return super(AccountInvoice, self).action_cancel_draft()

    @api.multi
    def action_cancel(self):
        """Cancel membership for customer invoices and restore previous
        membership state for customer refunds. Harmless on supplier ones.
        We detect dynamically if the module account_refund_original is
        installed for accurate source invoice.
        """
        # TODO: Module in v9 is `account_invoice_refund_link`
        self.mapped('invoice_line.membership_lines').write({
            'state': 'canceled',
        })
        refunds = self.filtered(lambda r: (
            r.type == 'out_refund' and
            # TODO: Rename this to `origin_invoice_ids` on v9
            (r.origin or getattr(r, 'origin_invoices_ids', False))
        ))
        for refund in refunds:
            # Search for the original invoice it modifies
            if hasattr(refund, 'origin_invoices_ids'):
                origins = refund.origin_invoices_ids
            else:
                # Try to match by origin string
                origins = self.search([
                    ('type', '=', 'out_invoice'),
                    ('number', '=', refund.origin),
                ])
            for origin in origins:
                lines = origin.mapped('invoice_line.membership_lines')
                if origin and lines:
                    origin_state = (
                        'paid' if origin.state == 'paid' else 'invoiced'
                    )
                    lines.filtered(lambda r: r.state == 'canceled').write({
                        'state': origin_state,
                    })
                    lines.write({
                        'date_cancel': False,
                    })
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def invoice_validate(self):
        self.mapped('invoice_line').mapped('membership_lines').write({
            'state': 'invoiced',
        })
        for refund in self.filtered(lambda r: r.type == 'out_refund'):
            origin = self.search([
                ('type', '=', 'out_invoice'),
                ('number', '=', refund.origin),
            ])
            lines = origin.mapped('invoice_line').mapped('membership_lines')
            if origin and lines:
                if origin.amount_untaxed == refund.amount_untaxed:
                    lines.write({
                        'state': 'canceled',
                        'date_cancel': refund.date_invoice,
                    })
                else:
                    lines.write({
                        'date_cancel': refund.date_invoice,
                    })
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def confirm_paid(self):
        self.mapped('invoice_line').mapped('membership_lines').write({
            'state': 'paid',
        })
        return super(AccountInvoice, self).confirm_paid()
