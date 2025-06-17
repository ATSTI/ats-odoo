# -*- coding: utf-8 -*-
#############################################################################

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commission_value = fields.Float('Comissão', digits=dp.get_precision('Account'),
                                readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.onchange('commission_value')
    def _onchange_comission_value(self):
        for order in self:
            if order.commission_value:
                value = order.amount_price_gross - order.commission_value
                # value_percent = (value * 100 / order.amount_price_gross) * -1
                # order.update({
                #     'amount_tax': value,
                # })
                # for line in order.order_line:
                #     line.ipi_percent = value_percent
                #     line.ipi_value = value
                #     # line.amount
                order.amount_other_value = value
                order.amount_total = order.commission_value
                order.amount_financial_total = order.commission_value

    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'commission_value': self.commission_value
        })
        return invoice_vals
    
    def _create_invoices(self, grouped=False, final=False, date=None):
        invoice = super()._create_invoices(grouped=grouped, final=final, date=date)
        invoice.comission = True
        invoice._onchange_comission_value()
        return invoice

    def button_dummy(self): 
        self._onchange_comission_value()
        return True
