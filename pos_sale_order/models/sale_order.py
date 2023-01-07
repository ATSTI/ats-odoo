# -*- coding:utf-8 -*-

from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_from_ui(self, orders):
        #gerava pedido de venda para cada pedido iniciado no pdv 
        order_ref = self.env['sale.order'].search([('name','=',orders['name'])])
        if order_ref:
            order_ref.write({'state': 'cancel'})
        order_id = self.create(orders)
        order_ref = orders['name']
        #return order_ref
        # estava comentado daqui pra baixo, a linha acima esta descomentada 06/09/19    
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        pos_order = self.search([('pos_reference', 'in', submitted_references)])
        existing_orders = pos_order.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        order_ids = []

        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            if to_invoice:
                self._match_payment_to_invoice(order)
            pos_order = self._process_order(order)
            order_ids.append(pos_order.id)

            try:
                pos_order.action_pos_order_paid()
            except psycopg2.OperationalError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice:
                pos_order.action_pos_order_invoice()
                pos_order.invoice_id.sudo().action_invoice_open()
                pos_order.account_move = pos_order.invoice_id.move_id
        return order_ids

