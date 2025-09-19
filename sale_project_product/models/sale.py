# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from collections import defaultdict
from odoo.addons.sale_project.models.sale_order_line import SaleOrderLine as ParentSaleOrderLine

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def _get_stage_id(self):
        for order in self:
            if not order.tasks_ids:
                order.task_stage = ''
            for tk in order.tasks_ids:
                order.task_stage = tk.stage_id.name
                
    
    task_stage = fields.Char(string='Estagio da Tarefa Engenharia', compute='_get_stage_id', readonly=True)
    libera = fields.Boolean(string="Entrega Liberada pelo Financeiro")

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_service_generation(self):
        # Reaplicar apenas a sua versão do bloco task_global_project
        so_lines = []
        prj_id = False
        so_line_task_global_project = self.filtered(
            lambda sol: sol.is_service and sol.product_id.service_tracking == 'task_global_project'
        )
        map_sol_project = {sol.id: sol.product_id.with_company(sol.company_id).project_id for sol in so_line_task_global_project}

        if so_line_task_global_project:
            for so_line in so_line_task_global_project:
                if not so_line.task_id and so_line.product_uom_qty > 0:
                    if not prj_id:
                        prj_id = so_line.product_id.project_id
                        so_lines.append(so_line)
                    else:
                        if prj_id.id == map_sol_project.get(so_line.id).id:
                            so_lines.append(so_line)
                        else:
                            so_line._timesheet_create_task(project=map_sol_project.get(so_line.id))
            if so_lines:
                so_lines[0]._timesheet_create_task(project=prj_id)
        return ParentSaleOrderLine._timesheet_service_generation(self)

                