# -*- coding: utf-8 -*-
# © 2020 Carlos Silveira, ATS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.exceptions import UserError

class ContasReceber(models.Model):
    _name = 'contas.receber'
    _description = 'Contas a Receber'
    _order = 'data_rec desc'

    name = fields.Char('Titulo')
    invoice_id = fields.Many2one('account.invoice', string='Fatura')
    valor_titulo = fields.Float(string='Valor Titulo')
    valor_recebido = fields.Float(string='Valor Recebido')
    data_recebido = fields.Date(string='Data Recebimento')
    caixa_recebeu = fields.Many2one('pos.session', string='Caixa')
    forma_pagamento = fields.Char('Forma Pagameto')
    
    
    @api.model
    def create(self, vals):
        res = super(ContasReceber, self).create(vals)
        inv = self.env['contas.receber'].browse([res.invoice_id.id])
        if inv and inv.state != 'open':
            return res
            
        jrn = '1-'
        # cartao Credito ATSAdmin    
        if res.forma_pagamento == '6':
            jrn = '3-'
        # cartao Debito ATSAdmin
        if res.forma_pagamento == '7':
            jrn = '2-'
        jrn_id = self.env['account.journal'].search([
            ('name','like', jrn)])[0]
        stmt = res.caixa_recebeu.cash_register_id
        if jrn != '1-':
            stmt = self.env['account.bank.statement'].search([
                ('journal_id','=', jrn_id.id),
                ('pos_session_id','=', res.caixa_recebeu.id),
            ])
        lancado_id = self.env['account.bank.statement.line'].search([
            ('move_name','=',res.name),
            ('statement_id','=', stmt.id),
            ('journal_id','=', jrn_id.id),
        ])
        if lancado_id:
            # ja peguei a fatura la em cima nao preciso
            #faturas_ids = self.env['account.invoice'].search([
            #   ('partner_id','=', rcs[6]),
            #   ('origin', '=', ppdv.name)
            #   ('state','=', 'open'),
            #])
            #for ftr in faturas_ids:
            inv.pay_and_reconcile(jrn_id.id, res.valor_recebido)
        else:    
            values = {}
            values['statement_id'] = stmt.id
            values['journal_id'] = jrn_id.id
            values['ref'] = res.caixa_recebeu.name
            values['move_name'] = str(res.titulo)
            values['name'] = 'Recebimento conta %s' %(res.titulo)
            values['amount'] = res.valor_recebido
            st_line = self.env['account.bank.statement.line'].create(values)                                        
            inv.pay_and_reconcile(jrn_id.id, rcs[4])        
            move_line = inv.move_id.line_ids.filtered(
                lambda r: r.account_id.id == inv.account_id.id
                )
            vals = {
                'name': st_line.name,
                'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                'credit': st_line.amount > 0 and st_line.amount or 0.0,
                'move_line': move_line
            }
            st_line.process_reconciliation(counterpart_aml_dicts=[vals])
        return res
