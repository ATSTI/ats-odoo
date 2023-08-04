# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _, tools


class BalanceReport(models.AbstractModel):
    _name = 'report.report_sale_balance.balance_report'
    _description = 'Relatorio Vendas/Compras'

    def _get_report_values(self, docids, data=None):
        t_out = self.env['sale.order'].search([
            ("commitment_date", ">=", data['data']['date_start']),
            ("commitment_date", "<=", data['data']['date_end'])])
        t_in = self.env['purchase.order'].search([
            ("commitment_date", ">=", data['data']['date_start']),
            ("commitment_date", "<=", data['data']['date_end'])])
        prod_ids = t_out.order_line.mapped("product_id")
        itens = []
        for pr in prod_ids:
            vals = {}
            p_out = sum(
                line.product_uom_qty for line in t_out.order_line.filtered(
                    lambda x: x.product_id.id in [pr.id]
               )
            )
            p_in = sum(
                line.product_uom_qty for line in t_in.order_line.filtered(
                    lambda x: x.product_id.id in [pr.id]
               )
            )
            d = data['data']['date_start']
            date_in = f"{d[8:10]}/{d[5:7]}/{d[:4]}"
            d = data['data']['date_end']
            date_end =  f"{d[8:10]}/{d[5:7]}/{d[:4]}"
            vals['product_id'] = pr.id
            vals['name'] = f"[{pr.default_code}]{pr.name}"
            vals['preco'] = pr.lst_price
            vals['unidade'] = pr.uom_id.code
            vals['venda'] = p_out
            vals['compra'] = p_in
            vals['saldo'] = p_in - p_out
            vals['date_start'] = date_in
            vals['date_end'] = date_end
            itens.append(vals)

        return {
            'docs': itens,
        }
