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
    
    entrega_liberada_stock = fields.Boolean(string='Entrega Liberada', related='sale_id.libera', readonly=True)
    status_tarefa = fields.Char(string='ESTAGIO DA TAREFA ENGENHARIA', related='sale_id.task_stage', readonly=True)
    tasks_count_stock = fields.Integer(string='Tarefas', related='sale_id.tasks_count')
    mrp_production_count_stock = fields.Integer(string='Tarefas', related='sale_id.mrp_production_count')

    def action_chama_taks(self):
        # import pudb;pu.db
        action = self.sale_id.action_view_task()
        return action
    
    def action_chama_mrp(self):
        # import pudb;pu.db
        action = self.sale_id.action_view_mrp_production()
        return action
        
