# -*- coding:utf-8 -*-

from odoo import models, fields, api, tools, _
# from odoo.addons.point_of_sale.wizard.pos_box import PosBox
# from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
# from unidecode import unidecode
import logging
import odoorpc


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def enviando_picking(self):
        # Example: Get the value of the 'web.base.url' parameter
        # 'key' is the unique identifier for the parameter (e.g., 'web.base.url')
        # 'default_value' is optional and what will be returned if the key is not found (defaults to None)
        config_port = self.env['ir.config_parameter'].sudo().get_param('stock_picking.port')
        config_user = self.env['ir.config_parameter'].sudo().get_param('stock_picking.user')
        config_passwd = self.env['ir.config_parameter'].sudo().get_param('stock_picking.passwd')
        config_url = self.env['ir.config_parameter'].sudo().get_param('stock_picking.url')
        destino = odoorpc.ODOO(config_url, port=config_port)
        destino.login('felicita8', config_user, config_passwd)
        stq_dest = destino.env['stock.picking']

        # buscar picking que ainda não foram enviados
        stq_origem = self.env['stock.picking'].search([('location_dest_id', '=', 43), ('state', '=', 'done'),], order="id desc", limit=2)
        
        
        for st in stq_origem:
            # verificar se ja foi enviado
            stq_pick = stq_dest.search([('name', '=', st.name)])
            if not stq_pick:               
                pick = stq_dest.create({
                    'name': st.name,
                    'origin': st.origin,
                    'location_id': 19,  # Estoque Felicita
                    'location_dest_id': 8, # Estoque local
                    'picking_type_id': 5, # Transferencia interna
                })
                for line in st.move_ids_without_package:
                    prod = stq_dest.env['product.product'].search([('default_code', '=', line.product_id.default_code)], limit=1)[0]
                    if not prod:
                        prod = stq_dest.env['product.product'].create({
                            'name': line.product_id.name,
                            'default_code': line.product_id.default_code,
                            'type': 'product',
                            'categ_id': 1, # Categoria de produto
                            'list_price': line.product_id.list_price,
                            'standard_price': line.product_id.standard_price,
                            'uom_id': line.product_uom.id,
                        }).id
                    item = [(0, 0, {
                        'product_id': prod,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'quantity_done': line.quantity_done,
                        'name': line.name,
                        'location_id': 19,  # Estoque Felicita
                        'location_dest_id': 8, # Estoque local
                    })],
                    stq_pick = stq_dest.env['stock.picking'].browse(pick)
                    stq_pick.write({
                        'move_ids_without_package': item
                    })
        return True    
