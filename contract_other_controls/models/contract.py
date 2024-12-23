# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date


class ContractContract(models.Model):
    _inherit = 'contract.contract'

       
    msg_faturamento = fields.Char(u'Mensagem Faturamento')
    envia_email = fields.Boolean(string='Envia por Email')
    
    @api.depends('date_start')
    def _compute_vencimento(self):
        self.mes_contrato = self.date_start.month
        self.ano_contrato = self.date_start.year
    
    mes_contrato = fields.Integer(string='Mes Contrato',
        store=True, readonly=True, compute='_compute_vencimento')
    ano_contrato = fields.Integer(string='Ano Contrato',
        store=True, readonly=True, compute='_compute_vencimento')    

    def tempo(self, mes, ano):
        dt = date.today()
        mes_atual = dt.month
        ano_atual = dt.year
        soma_mes = 0
        if mes < mes_atual:
            ano_atual -= 1
            soma_mes = mes - mes_atual
        else:
            soma_mes = mes_atual - mes
        tempo = ((ano_atual - ano) * 12) + soma_mes
        return str(tempo)


    @api.model
    def _prepare_invoice(self, date_invoice, journal=None ):
        vals = super(ContractContract, self).\
            _prepare_invoice(date_invoice)
        for invoice_vals in vals:
            if not isinstance(invoice_vals, dict):
                continue
            today = date.today()
            tempo = self.tempo(self.mes_contrato, self.ano_contrato)
            if tempo == "0":
                tempo = str(self.id)
            invoice_vals['ref'] = '%s(%s)-%s-%s' %(
                self.name, tempo, str(today.month).zfill(2), today.year)
            if not invoice_vals['partner_id']:
                invoice_vals['partner_id'] = self.partner_id.id 
        return vals
