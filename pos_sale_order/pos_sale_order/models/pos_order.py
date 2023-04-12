# -*- coding:utf-8 -*-

from odoo import models, api, tools, _
from odoo.exceptions import UserError
import logging
import psycopg2

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _payment_fields(self, ui_paymentline):
        import pudb;pu.db
        if 'date' in ui_paymentline:
            dt = ui_paymentline['date']
        else:
            dt = ui_paymentline['name']

        return {
            'amount':       ui_paymentline['amount'] or 0.0,
            'payment_date': dt,
            'statement_id': ui_paymentline['statement_id'],
            'payment_name': ui_paymentline.get('note', False),
            'journal':      ui_paymentline['journal_id'],
        }

    @api.model
    def create_order(self, orders, order):
        # Keep only new orders
        order_ids = []
        to_invoice = False
        for stm in orders:
            if stm[2]['journal_id'] == 10:
                to_invoice = True
            amount = order.amount_total - order.amount_paid
            data = stm[2]
            #data['journal'] = data[2]['journal_id']
            if amount != 0.0:
                order.add_payment(data)
            if order.test_paid():
                order.action_pos_order_paid()        
            
        if to_invoice:
            #import pudb;pu.db
            #orders['amount_return'] = orders[0][2]['amount']
            #self._match_payment_to_invoice(orders[0][2])
            order.action_pos_order_invoice()
            order.invoice_id.sudo().action_invoice_open()
        #pos_order = self._process_order(orders)
        #order_ids.append(pos_order.id)
        
        

        #try:
        #    pos_order.action_pos_order_paid()
        #except psycopg2.OperationalError:
        #    # do not hide transactional errors, the order(s) won't be saved!
        #    raise
        #except Exception as e:
        #    _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

        #if to_invoice:
        #    pos_order.action_pos_order_invoice()
        #    pos_order.invoice_id.sudo().action_invoice_open()
        #    pos_order.account_move = pos_order.invoice_id.move_id
    

    @api.model
    def create(self, values):
        """ gerava pedido de venda para cada pedido iniciado no pdv 
        order_ref = self.env['sale.order'].search([('name','=',orders['name'])])
        if order_ref:
            order_ref.write({'state': 'cancel'})
        order_id = self.create(orders)
        order_ref = orders['name']
        return order_ref
        """
        # Keep only new orders
        #import pudb;pu.db
        """
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
        """
        """
        to_invoice = False
        for stm in values['statement_ids']:
            if stm[2]['journal_id'] == 10:
                self._match_payment_to_invoice(values)
                to_invoice = True
            pos_order = self._process_order(values)
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
        """
        #import pudb;pu.db
        if 'pos_session_id' in values:
            stm_ids = values['statement_ids']
            del values['statement_ids']
            res = super(PosOrder, self).create(values)
            self.create_order(stm_ids, res)
        else:
            res = super(PosOrder, self).create(values)
        return res
