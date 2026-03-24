# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class CreateTaskWizard(models.TransientModel):
    _name = 'create.task.wizard'
    _description = 'Create Task in Project'

    project_id = fields.Many2one('project.project', string="Projeto", required=True)
    name = fields.Char(string="Nome", required=True, compute="compute_name", store=True)
    partner_id = fields.Many2one('res.partner', string="Parceiro", readonly=True)
    user_id = fields.Many2one('res.users', string="Atribuida a", default=lambda self: self.env.user)
    date_deadline = fields.Date(string="Data de Vencimento")

    description = fields.Text(
        string="Descrição",
        compute="_compute_description",
        store=True
    )

    @api.depends('project_id')
    def _compute_description(self):
        for record in self:
            if record.project_id and not record.description:
                desc = f"Tarefa Criada para o Projeto: {record.project_id.name}"
                for line in record.env['sale.order'].browse(record.res_id).order_line:
                    if line.product_id:
                        desc += f"\n- {line.product_id.name} (x{line.product_uom_qty})"
                record.description = desc

    @api.depends('project_id')
    def compute_name(self):
        for record in self:
            record.name = f"{record.env['sale.order'].browse(record.res_id).name} | {record.env['sale.order'].browse(record.res_id).user_id.name} |"

    def action_create_task(self):
        self.ensure_one()
        if not self.project_id:
            raise UserError(_("Porfavor selecione um projeto."))
        
        task_vals = {
            'name': self.name,
            'project_id': self.project_id.id,
            'user_ids': [1,(self.user_id.id)],
            'date_deadline': self.date_deadline,
            'description': self.description,
            'sale_order_id': self.res_id,
        }
        task = self.env['project.task'].create(task_vals)
        self.env['sale.order'].browse(self.res_id).write({'tasks_ids': [(4, task.id)]})
        self.env['sale.order'].browse(self.res_id).write({'tasks_ids': [(4, self.project_id.id)]})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Task Created'),
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': task.id,
            'target': 'current',
        }

    model = fields.Char('Related Document Model')
    res_id = fields.Integer('Related Document ID')