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
    
    task_stage = fields.Char(string='Estagio da Tarefa Engenharia', compute='_get_stage_id', readonly=True)
    libera = fields.Boolean(string="Entrega Liberada pelo Financeiro")

    # def _get_entrega_liberada(self):
    #     for order in self:
    #         order.entrega_liberada = False
    #         for fat in order.invoice_ids:
    #             if fat.state == 'cancel':
    #                 continue
    #             if self.libera == True:
    #                 order.entrega_liberada = self.libera
    #         # self.entrega_liberada = False 
    
    # entrega_liberada = fields.Boolean(string='Entrega Liberada', compute='_get_entrega_liberada', readonly=True)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        self.ensure_one()
        planned_hours = self._convert_qty_company_hours(self.company_id)
        sale_line_name_parts = self.name.split('\n')
        title = sale_line_name_parts[0] or self.product_id.name
        description = ''
        return {
            'name': title if project.sale_line_id else '%s: %s' % (self.order_id.name or '', title),
            'planned_hours': planned_hours,
            'partner_id': self.order_id.partner_id.id,
            'email_from': self.order_id.partner_id.email,
            'description': description,
            'project_id': project.id,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id.id,
            'company_id': project.company_id.id,
            'user_id': False,  # force non assigned task, as created as sudo()
        }

    @api.depends('product_id.type')
    def _compute_is_service(self):
        for so_line in self:
            so_line.is_service = True