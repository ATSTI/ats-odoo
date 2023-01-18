# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from datetime import date, datetime


class ExecutarFaturamento(models.TransientModel):

    _name = "executar.faturamento"
    _description = "Faturar Contratos"

    @api.depends('grupo')
    def compute_buscar_grupo(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        if self.grupo and self.data_faturar:
            order_ids = self.env['contract.contract'].search([
                ('grupo', '=', self.grupo.id),
                ('date_start', '<=', self.data_faturar),
                ('date_end', '>=', self.data_faturar)
            ])
            self.buscar_grupo = 'Numero de Contratos a ser faturados: %s.' %(str(len(order_ids)))
        else:
            self.buscar_grupo = 'Sem grupo para faturar.'   

    grupo = fields.Many2one(
        comodel_name="obito.grupo",
        string="Grupo")

    data_faturar = fields.Date('Data') 

    plano = fields.Many2one(
        comodel_name="contract.plano",
        string="Plano")
    
    cobranca = fields.Many2one(
        comodel_name="contract.cobranca",
        string="Cobrança")

    user_id = fields.Many2one('res.users', string='Responsaveis', ondelete='restrict')    
    
    buscar_grupo = fields.Char(string='Mensagem', compute='compute_buscar_grupo', readonly=True)

    def execute_faturamento(self):
        import pudb;pu.db
        if not self.data_faturar:
            raise UserError(_("Porfavor prencher campo Data inicial."))
        domain = []
        if self.grupo.id: 
            domain = [('grupo', '=', self.grupo.id)]
        if self.data_faturar:
            domain += [('date_start', '<=', self.data_faturar)]
            domain += [('date_end', '>=', self.data_faturar)]
        if self.plano:
            domain += [('plano', '=', self.plano.id)]
        if self.cobranca:
            domain += [('cobranca', '=', self.cobranca.id)]
        if self.user_id:
            domain += [('user_id', '=', self.user_id.id)]      
        order_ids = self.env['contract.contract'].search(domain)
        for ctr in order_ids:
            ctr.recurring_create_invoice()
