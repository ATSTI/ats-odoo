# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    discount_type = fields.Selection(
        [('percent', 'Percentual'),
         ('amount', 'Quantia')],
        string='Tipo de Desconto',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
        default='percent')

    discount_value = fields.Float(
        string='Desconto',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]})

    @api.onchange('discount_value')
    def _onchange_discount_value(self):
        self.update_discount_lines()
        
    @api.depends('order_line.price_total', 'order_line.valor_desconto')
    def _amount_all(self):
        precision_discount = dp.get_precision('Discount')(self._cr)[1]
        precision_money = dp.get_precision('Product Price')(self._cr)[1]
        super(PurchaseOrder, self)._amount_all()

        for order in self:
            desconto_itens = 0.0
            for line in order.order_line:
                if line.discount:
                    discount_percent = line.discount
                    desconto_itens = round(discount_percent / 100 * line.valor_bruto,
                                precision_money)
                    line.valor_desconto = desconto_itens          
            price_total = sum(l.price_total for l in order.order_line)
            price_subtotal = sum(l.price_subtotal for l in order.order_line)
            # 'total_ipi': sum(l.ipi_valor for l in order.order_line),
            #                'total_icms_st': sum(l.icms_st_valor
            #                         for l in order.order_line),
            
            order.update({
                'total_tax': price_total - price_subtotal,
                'total_desconto': sum(l.valor_desconto
                                      for l in order.order_line),
                'total_bruto': sum(l.valor_bruto
                                   for l in order.order_line),
                'amount_total': price_subtotal,
            })
        #if price_subtotal:
        #    self.write({'amount_total': price_subtotal})

    def get_balance_line(self):
        for item in reversed(self.order_line):
            if item.valor_bruto:
                return item

    @api.multi
    def update_discount_lines(self):
        precision_discount = dp.get_precision('Discount')(self._cr)[1]
        precision_money = dp.get_precision('Product Price')(self._cr)[1]
        for item in self:
            # limpando desconto nos itens
            # qdo colocava zero no desconto total tinha que 
            # limpar dos itens manualmente
            if not item.discount_value:
                for line in item.order_line:
                    line.discount = 0.0
                continue            
            # verifica se tem desconto itens
            desconto_itens = 0.0
            vlr_desconto = 0.0
            for line in item.order_line:
                if line.discount:
                    discount_percent = line.discount
                    desconto_itens += round(discount_percent / 100 * line.valor_bruto,
                                precision_money)
                    vlr_desconto = desconto_itens
            balance_line = item.get_balance_line()

            # tem desconto no geral
            if item.discount_value:
                balance_line = item.get_balance_line()
                if not balance_line:
                    continue
                if item.discount_type == 'percent':
                    # preciso saber o percentual ja dado no produto
                    if  desconto_itens > 0.0:
                        discount_percent = round(
                            (desconto_itens / item.amount_total) * 100 + item.discount_value,
                            precision_discount) 
                    else:
                        discount_percent = round(item.discount_value,
                            precision_discount)        
                    vlr_desconto = round(item.amount_total * (discount_percent/100),precision_money)
                    discount_percent = round((vlr_desconto / item.total_bruto) * 100, precision_discount)
                if item.discount_type == 'amount':
                    vlr_desconto = item.discount_value + desconto_itens
                    discount_percent = round(
                        vlr_desconto / item.total_bruto * 100,
                        precision_discount)
                if discount_percent > 100:
                    discount_percent = 100
                elif discount_percent < 0:
                    discount_percent = 0
                    
                # nao calcular novamente
                if (balance_line.valor_desconto > 0.0) and \
                    ((vlr_desconto - balance_line.valor_desconto) < 0.01):
                    break                    
                for line in item.order_line:
                    line.discount = discount_percent
                balance_line.discount = discount_percent
                balance_line.valor_desconto = vlr_desconto
