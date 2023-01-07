# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import datetime


class account_abstract_payment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    def lanca_sangria_reforco(self, journal_id, caixa, valor, cod_forma, cod_venda, partner_id, motivo=''):
        # Inseri no PDV a Entrada no CAIXA
        lancamento = 'Recebimento-%s-%s' %(caixa, journal_id.name)
        if cod_venda == 0:
            lancamento = motivo
        if cod_venda == 1:
            lancamento = motivo
            valor = valor * (-1)
        hj = datetime.now()
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        session = self.env['pos.session'].search([
            ('id', '=', caixa)])
        for ses in session: 
            vals = {
                'date': hj,
                'amount': valor,
                'name': lancamento,
                'ref': str(cod_forma),
            }
            if partner_id:
                vals['partner_id'] = partner_id.id
            ja_importou = self.env['account.bank.statement.line'].search([
                ('ref', '=', str(cod_forma))])
            if ja_importou:
                continue
            for cx in ses.statement_ids:
                if cx.journal_id.id == journal_id.id:
                    stt = cx
                    jrn = cx.journal_id
                    vals['statement_id'] = cx.id
                    vals['journal_id'] = jrn.id
                    vals['account_id'] = jrn.company_id.transfer_account_id.id,
                    cx.write({'line_ids': [(0, False, vals)]})    


    def baixa_pagamentos(self, move_line_id, journal_id, caixa, valor, cod_forma, juros):
        invoices = move_line_id.invoice_id
        # amount = self._compute_payment_amount(invoices=invoices) if self.multi else self.amount
        if move_line_id.amount_residual > valor or ((move_line_id.amount_residual - valor) > 0.01):
            baixar_tudo = 'open'
        else:
            baixar_tudo = 'reconcile'
        bank_account = invoices[0].partner_bank_id or self.partner_bank_account_id
        # pmt_communication = self._prepare_communication(invoices)

        payment_type = 'inbound'# if move_line_id.debit else 'outbound'
        payment_methods = \
            payment_type == 'inbound' and \
            journal_id.inbound_payment_method_ids or \
            journal_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        conta_juros = ''
        juros_desc = ''
        if juros:
            cc = self.env['account.account'].search([
                    ('name', 'ilike', 'Juros Recebidos'),
                    ('company_id', '=', journal_id.company_id.id),
            ])
            conta_juros = cc.id
            juros_desc = 'Juros recebido %s - %s' %(move_line_id.partner_id.name, move_line_id.name or '')
        vals = {
            'journal_id': journal_id.id,
            'payment_method_id': payment_method_id.id,
            'payment_date': datetime.now(),
            'communication': invoices.name,
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': payment_type,
            'amount': valor+juros,
            'currency_id': journal_id.company_id.currency_id.id,
            'partner_id': move_line_id.partner_id.id,
            'partner_type': 'customer',
            'partner_bank_account_id': bank_account.id,
            'multi': False,
            'payment_difference_handling': baixar_tudo,
            'writeoff_account_id': conta_juros,
            'writeoff_label': juros_desc
        }
        Payment = self.env['account.payment']        
        pay = Payment.create(vals)
        pay.post()
        # coloco o valor no PDV como uma entrada
        # pra nao dar diferenca no caixa
        self.lanca_sangria_reforco(journal_id, caixa, valor+juros, cod_forma, cod_forma, move_line_id.partner_id, invoices.name)
