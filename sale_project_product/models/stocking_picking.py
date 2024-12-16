# -*- encoding: utf-8 -*-

from odoo import fields, models, _, api

class StockPicking(models.Model): 
    _inherit = "stock.picking"


    # def _get_entrega_liberada(self):
    #     for order in self:
    #         order.entrega_liberada = False
    #         for fat in order.invoice_ids:
    #             if fat.libera == True:
    #                 order.entrega_liberada = fat.libera
    #         # self.entrega_liberada = False 
    
    entrega_liberada_stock = fields.Boolean(string='Entrega Liberada', related='sale_id.entrega_liberada', readonly=True)
        
