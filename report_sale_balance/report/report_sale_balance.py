# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _, tools


class BalanceReport(models.AbstractModel):
    _name = 'report.report_sale_balance.balance_report'
    _description = 'Relatorio Vendas/Compras'

    def _get_report_values(self, docids, data=None):
        import pudb;pu.db
        t_out = self.env['sale.order'].search([
            ("date_order", ">=", data['data']['date_start']),
            ("date_order", "<=", data['data']['date_end'])])
        t_in = self.env['purchase.order'].search([
            ("date_order", ">=", data['data']['date_start']),
            ("date_order", "<=", data['data']['date_end'])])
        x = 0.0
        for s in t_out.order_line:
            print(f"{s.product_id.id}: {s.product_uom_qty}")
        prod_ids = t_out.order_line.mapped("product_id")
        qty = t_out.order_line.mapped("product_uom_qty")
        list_prod = set()
        # for pr in prod_ids:
        #     p_out = sum(
        #         line.product_uom_qty for line in t_out.order_line.filtered(
        #             lambda x: x.product_id in [pr.id]
        #     ))            
        # for s in t_out.order_line:
        #     list_prod.add(s.product_id.id)
        #     self.sum_of_credit = sum(
        #         line.credit for line in self.order_line.filtered(
        #             lambda x: x.account_id.user_type_id.type in ['cash', 'bank']
        #     ))

        sum_out = 1
        sale_purchase_obj = self.env['sale.purchase.balance']
        itens = []
        vals = {}
  
            # vals['product_id'] = s.product_id.id
            # vals['venda'] = s.product_uom_qty

        
        # sale_purchase_obj.create{
        #     'product_id'
        # }        
        # data['sale_id'] = data.get('id', docids)
        # data['warehouse_ids'] = data.get('warehouse_ids', [])
        # sale = self.env['sale.order'].browse(data['context']['active_ids'])
        docs = self.env['sale.order'].search([("date_order", ">=", data['data']['date_start']),("date_order", "<=", data['data']['date_end'])])
        return {
            'docs': docs,
        }
    

class SalePurchaseBalance(models.AbstractModel):
    _name = 'sale.purchase.balance'
    _description = 'Saldo Vendas/Compras'

    product_id = fields.Many2one(
        'product.product', 'Product')
    venda = fields.Float('Total Venda')
    compra = fields.Float('Total Compra')
    saldo = fields.Float('Venda-Compra')

    # @api.depends('product_id')
    # def _compute_product_qty(self):
    
#     def init(self):
#         tools.drop_view_if_exists(self._cr, 'report_stock_quantity')
#         query = """
# CREATE or REPLACE VIEW sale_purchase_balance AS (
# WITH
#     existing_sm (id, product_id, venda, compra, saldo) AS (
#     SELECT s.id, s.product_id, s.product_uom_qty, 
#     """
#         self.env.cr.execute(query)