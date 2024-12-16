# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def _get_stage_id(self):
        for order in self:
            if order.tasks_ids:
                order.task_stage = order.tasks_ids.stage_id.name
            else:
                order.task_stage = ''
    
    task_stage = fields.Char(string='Estágio da Tarefa', compute='_get_stage_id', readonly=True)

    def _get_entrega_liberada(self):
        for order in self:
            order.entrega_liberada = False
            for fat in order.invoice_ids:
                if fat.state == 'cancel':
                    continue
                if fat.libera == True:
                    order.entrega_liberada = fat.libera
            # self.entrega_liberada = False 
    
    entrega_liberada = fields.Boolean(string='Entrega Liberada', compute='_get_entrega_liberada', readonly=True)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id.type')
    def _compute_is_service(self):
        for so_line in self:
            so_line.is_service = True