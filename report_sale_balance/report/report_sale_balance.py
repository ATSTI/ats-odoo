# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import fields, api, models, _, tools


class BalanceReport(models.AbstractModel):
    _name = 'report.report_sale_balance.balance_report'
    _description = 'Relatorio Vendas/Compras'

    def _get_report_values(self, docids, data=None):
        date_start = datetime.strptime(
            '%s 00:01:00' %(data['data']['date_start']), "%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
        # date_start = fields.Datetime.context_timestamp(self, document_date)
        date_end = datetime.strptime(
            '%s 23:59:00' %(data['data']['date_end']), "%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
        # date_end = fields.Datetime.context_timestamp(self, document_date)
        t_out = self.env['sale.order'].search([
            ("commitment_date", ">=", date_start),
            ("commitment_date", "<=", date_end)])
        t_in = self.env['purchase.order'].search([
            ("date_planned", ">=", date_start),
            ("date_planned", "<=", date_end)])
        
        prod_out = t_out.order_line.mapped("product_id")
        prod_in = t_out.order_line.mapped("product_id")
        prod_ids = set()
        for p in prod_out.ids:
            prod_ids.add(p)
        for p in prod_in.ids:
            prod_ids.add(p)
        itens = []
        for pr in list(prod_ids):
            vals = {}
            prod = self.env['product.product'].browse([pr])
            p_out = sum(
                line.product_uom_qty for line in t_out.order_line.filtered(
                    lambda x: x.product_id.id in [prod.id]
               )
            )
            p_in = sum(
                line.product_uom_qty for line in t_in.order_line.filtered(
                    lambda x: x.product_id.id in [prod.id]
               )
            )
            d = data['data']['date_start']
            date_in = f"{d[8:10]}/{d[5:7]}/{d[:4]}"
            d = data['data']['date_end']
            date_end =  f"{d[8:10]}/{d[5:7]}/{d[:4]}"
            vals['product_id'] = prod.id
            vals['name'] = f"[{prod.default_code}]{prod.name}"
            vals['prod'] = prod.name
            vals['preco'] = prod.lst_price
            vals['unidade'] = prod.uom_id.code
            vals['venda'] = p_out
            vals['compra'] = p_in
            vals['saldo'] = p_in - p_out
            vals['date_start'] = date_in
            vals['date_end'] = date_end
            itens.append(vals)
        itens_ordem = sorted(itens,key=lambda k: k['prod'])
        return {
            'docs': itens_ordem,
        }
