# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_city = fields.Char(
        string="Cidade",
        related="partner_id.city",
        store=True,
        readonly=True,
    )

    partner_state_id = fields.Many2one(
        "res.country.state",
        string="Estado",
        related="partner_id.state_id",
        store=True,
        readonly=True,
    )

    contact_partner = fields.Many2many(
        comodel_name='res.partner',
        compute='_compute_contact_partner',
        string='Contatos do Parceiro',
        store=False)

    contact_partner_names = fields.Char(
        string='Contatos do Parceiro',
        compute='_compute_contact_partner_names',
        store=False)

    message_error_partner = fields.Char(
        string='Mensagem de erro do parceiro',
        readonly=True,
        invisible=True)
    
    task_stage = fields.Char(string='Estagio da Tarefa Engenharia', compute='_get_stage_id', readonly=True)

    def _get_stage_id(self):
        for order in self:
            if not order.tasks_ids:
                order.task_stage = ''
            for tk in order.tasks_ids:
                order.task_stage = tk.stage_id.name

    @api.depends('partner_id')
    def _compute_contact_partner(self):
        for order in self:
            if order.partner_id:
                # Só contatos ativos (e sem empresas)
                contacts = order.partner_id.child_ids.filtered(lambda c: c.active)
                order.contact_partner = contacts
            else:
                order.contact_partner = [(5, 0, 0)]

    @api.depends('contact_partner')
    def _compute_contact_partner_names(self):
        for order in self:
            names = order.contact_partner.mapped('name')
            order.contact_partner_names = ', '.join(names)
    
    def action_confirm(self):
        result = super().action_confirm()
        self.message_error_partner = False
        if self.partner_id and self.fiscal_operation_id:
            max = ""
            if self.partner_id.street_name and self.partner_id.district:
                max = self.partner_id.street_name or "" + self.partner_id.street2 or "" + self.partner_id.district or ""
            # tratar erros
            erros = ""
            if not self.partner_id.legal_name:
                erros += "\n Cadastro do parceiro sem Razão social."
            if not self.partner_id.cnpj_cpf:
                erros += "\n Cadastro do parceiro sem CNPJ/CPF."
            if not self.partner_id.zip:
                erros += "\n Cadastro do parceiro sem CEP."
            if self.partner_id.zip:
                cep = re.sub('[^0-9]', '', self.partner_id.zip)
                if not len(cep) == 8:
                    erros += "\n CEP errado no cadastro."
            if not self.partner_id.street_name:
                erros += "\n Cadastro do parceiro sem Rua."
            if not self.partner_id.street_number:
                erros += "\n Cadastro do parceiro sem NÚMERO."
            if not self.partner_id.district:
                erros += "\n Cadastro do parceiro sem Bairro."
            if not self.partner_id.city_id:
                erros += "\n Cadastro do parceiro sem CIDADE."
            if self.partner_id.phone:
                fone = re.sub('[^0-9]', '', self.partner_id.phone)
                if len(fone) > 13:
                    erros += "\n Número de telefone inválido."
            if len(max) > 60:
                erros += "\n Rua + Bairro + Complemento deve ser menor que 60 caracteres."
            if self.partner_id.name and len(self.partner_id.name) > 60:
                erros += "\n Nome deve ser menor que 60 caracteres."
            if self.partner_id.legal_name and len(self.partner_id.legal_name) > 60:
                erros += "\n Razão social deve ser menor que 60 caracteres."
            # if self.fiscal_operation_id.name and len(self.fiscal_operation_id.name) > 60:
            #     erros += "\n Natureza da operação deve ser menor que 60 caracteres."

            # erros = "\n".join(erros)
            self.message_error_partner = erros or False
            if self.message_error_partner:
                raise models.ValidationError(
                    _("Erro no cadastro do parceiro: %s") % self.message_error_partner
                )
        return result
    
    def action_create_task(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Task in Project'),
            'res_model': 'create.task.wizard',  
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_project_id': self.project_id.id if self.project_id else self.env['project.project'].browse(1).id,
                'default_model': 'sale.order',
                'default_res_id': self.id,
            },
        }