# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import datetime


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def lanca_sangria_reforco(self, journal_id, caixa, valor, cod_forma, cod_venda, partner_id, motivo=''):
        # Inseri no PDV a Entrada no CAIXA
        #import wdb
        #wdb.set_trace()  
        lancamento = 'Recebimento-%s-%s' %(caixa, journal_id.name)
        if cod_venda == 0:
            lancamento = motivo
        if cod_venda == 1:
            lancamento = motivo
            valor = valor * (-1)
        hj = datetime.now()
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        session = f"/{caixa}"
        session_id = self.env['pos.session'].sudo().search([('name', 'ilike', session)])
        for ses in session_id: 
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
                    vals['payment_ref'] = motivo # corrigi 06/07/23
                    self.env['account.bank.statement.line'].sudo().create(vals)

    def baixa_pagamentos(self, move_line_id, journal_id, caixa, valor, cod_forma, juros):
        invoices = move_line_id.move_id
        if move_line_id.amount_residual > valor and ((move_line_id.amount_residual - valor) > 0.01):
            baixar_tudo = 'open'
        else:
            baixar_tudo = 'reconcile'

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
        # vals = {
        #     'journal_id': journal_id.id,
        #     'payment_method_id': payment_method_id.id,
        #     #'payment_date': datetime.now(),
        #     'payment_reference': invoices.name,
        #     # 'move_id': invoices.id,
        #     'payment_type': payment_type,
        #     'amount': valor+juros,
        #     'currency_id': journal_id.company_id.currency_id.id,
        #     'partner_id': move_line_id.partner_id.id,
        #     'partner_type': 'customer',
        #     # 'payment_difference_handling': baixar_tudo,
        #     # 'writeoff_account_id': conta_juros,
        #     # 'writeoff_label': juros_desc
        # }
        apr = self.env['account.payment.register']
        to_process = []
        payment_vals = {
            'date': datetime.now(),
            'amount': valor,
            'payment_type': payment_type,
            'partner_type': 'customer',
            'ref': invoices.name,
            'journal_id': journal_id.id,
            'currency_id': journal_id.company_id.currency_id.id,
            'partner_id': move_line_id.partner_id.id,
            'payment_method_id': payment_method_id.id,
            'destination_account_id': move_line_id.account_id.id,
        }

        if juros and baixar_tudo == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': juros_desc,
                'amount': juros,
                'account_id': conta_juros,
            }

        to_process.append({
            'create_vals': payment_vals,
            'to_reconcile': move_line_id,
            'batch': invoices,
        })

        apr._init_payments(to_process, edit_mode=True)
        apr._post_payments(to_process, edit_mode=True)
        apr._reconcile_payments(to_process, edit_mode=True)

        """
        # TODO - Funciona sem o Juros

        ap_id = self.env['account.payment'].create(vals)
        ap_id.write({'reconciled_invoice_ids': [(4, invoices.id)]})
        ap_id.action_post()
        invoices.ensure_one()
        lines = ap_id.move_id.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        lines += invoices.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
        lines.reconcile()
        """
        # coloco o valor no PDV como uma entrada
        # pra nao dar diferenca no caixa
        self.lanca_sangria_reforco(journal_id, caixa, valor+juros, cod_forma, cod_forma, move_line_id.partner_id, invoices.name)
