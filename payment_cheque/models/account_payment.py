# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class account_payment(models.Model):
    _inherit = "account.payment"

    cheque_barra = fields.Char(string='Leitura Cheque')
    cheque = fields.Char(string='Número Cheque', readonly=True)
    comp = fields.Char(string='Comp.', readonly=True)
    banco = fields.Char(string='Banco', readonly=True)
    agencia = fields.Char(string='Agencia', readonly=True)
    conta = fields.Char(string='Conta', readonly=True)
    e_cheque = fields.Boolean(compute='_compute_e_cheque', help='Verifica se o diário usado é de cheque, code = chk')
    
    @api.depends('journal_id')
    def _compute_e_cheque(self):
        if self.journal_id:
            self.e_cheque = False
            if self.journal_id.code == 'chk':
                self.e_cheque  = True
    
    
    @api.onchange('cheque_barra')
    def _onchange_cheque_barra(self):
        if self.cheque_barra:
            self.cheque = self.cheque_barra[13:19].lstrip("0")
            self.comp = self.cheque_barra[10:13]
            self.banco = self.cheque_barra[1:4]
            self.agencia = self.cheque_barra[4:8]
            self.conta = self.cheque_barra[4:8]
            self.conta = self.cheque_barra[22:32].lstrip("0")
            self.communication = 'Cheque: %s-%s-%s-%s' %(
               self.cheque,
               self.banco,
               self.agencia,
               self.conta)
