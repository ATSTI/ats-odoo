# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date 


class PaymentAccountMoveLine(models.TransientModel):
    _inherit = 'payment.account.move.line'
 

    #@api.depends('amount', 'payment_date', 'currency_id')
    #def _compute_payment_difference(self):
    #    if self.amount > self.valor_original:
    #        self.payment_difference = self.amount - self.valor_original

    cheque_barra = fields.Char(string='Leitura Cheque')
    cheque = fields.Char(string='Número Cheque', readonly=True)
    comp = fields.Char(string='Comp.', readonly=True)
    banco = fields.Char(string='Banco', readonly=True)
    agencia = fields.Char(string='Agencia', readonly=True)
    conta = fields.Char(string='Conta', readonly=True)
    e_cheque = fields.Boolean(compute='_compute_e_cheque', help='Verifica se o diário usado é de cheque, code = chk')
    #payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
    #writeoff_account_id = fields.Many2one('account.account', string="Conta Diferença", domain=[('deprecated', '=', False)], copy=False) 
    #writeoff_label = fields.Char(
    #    string='Journal Item Label',
    #    default='')    

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


    """
    @api.model
    def default_get(self, fields):
        if 'move_line_id' in fields:
            rec = super(PaymentAccountMoveLine, self).default_get(fields)
        else:
            return super(AccountPayment, self).default_get(fields)
        move_line_id = rec.get('move_line_id', False)
        move_line = self.env['account.move.line'].browse(move_line_id)
        current_date = date.today()
        cpn = self.env['res.company.interest'].browse(move_line.company_id.id)
        if move_line.date_maturity >= current_date:
            rec.update({'valor_original': move_line.debit})
            return rec
        quantidade_dias = abs((current_date - move_line.date_maturity).days)
        if quantidade_dias < cpn.tolerance_interval:
            rec.update({'valor_original': move_line.debit})
            return rec
        quantidade_dias = quantidade_dias - cpn.tolerance_interval
        multa = move_line.debit * (cpn.multa/100)
        juros = cpn.company_id.currency_id.round(
            (cpn.rate/100) * quantidade_dias * move_line.debit)
        rec.update({
            'multa': multa,
            'juros': juros,
            'valor_original': move_line.debit,
        })

        return rec
    """ 
