# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time
from datetime import datetime
import base64

from odoo.addons.br_boleto.boleto.document import Boleto

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'


    @api.multi
    def _prepare_invoice_proprietario(self, proprietario, data_fatura=None):
        self.ensure_one()
        currency = (
            proprietario.partner_id.property_product_pricelist.currency_id or
            self.company_id.currency_id
        )
        invoice_type = 'in_invoice'
        payment_term_id = 1
        if proprietario.payment_term_id:
            payment_term_id = proprietario.payment_term_id.id
        fiscal_position_id = 2 # Pagamentos
        if not data_fatura:
            data_fatura = self.recurring_next_date
        else:
            data_fatura = datetime.strptime(data_fatura, '%Y-%m-%d')
        tempo = str(self.tempo(self.mes_contrato, self.ano_contrato))
        reference = '%s(%s)-%s-%s' %(
            self.name, tempo, 
            str(data_fatura.month).zfill(2),
            data_fatura.year)
        journal = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        invoice = self.env['account.invoice'].new({
            'payment_term_id': payment_term_id,
            'fiscal_position_id': fiscal_position_id,
            'reference': reference,
            'type': invoice_type,
            'partner_id': proprietario.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': data_fatura.strftime('%Y-%m-%d'),
            'origin': self.name,
            'company_id': self.company_id.id,
            'contract_id': self.id,
            'user_id': proprietario.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        if not invoice.payment_term_id:
            invoice.payment_term_id = payment_term_id
        if not invoice.fiscal_position_id:
            invoice.fiscal_position_id = fiscal_position_id
        return invoice._convert_to_write(invoice._cache)    

    def _prepare_order_lines_prop(self, contract, order_id, proprietario):
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            invoice_lines = []
            #if line.date_start and line.date_stop:
            #    if line.date_start <= self.recurring_next_date and line.date_stop > self.recurring_next_date:
            
            percent = 10
            if proprietario.percentual_aluguel:
                percent = proprietario.percentual_aluguel/100
            cota = 1
            if proprietario.cota:
                cota = proprietario.cota/100
            vlr = line.price_unit * line.quantity
            # ITEM ALUGUEL reduz comissao
            if line.product_id.id == 1:
                vlr = ((line.price_unit * line.quantity) *
                    ((1-percent) * cota))
            if line.repassa_prop:
                invoice_lines = {
                        'invoice_id': order_id.id,
                        'name': line.name,
                        'price_unit': vlr,
                        'uom_id': 1,
                        'quantity': 1,
                        'account_analytic_id': contract.id,
                        'product_id': line.product_id.id or False,
                        'account_id': line.product_id.categ_id.property_account_expense_categ_id.id
                }
            if len(invoice_lines):
                self.env['account.invoice.line'].create(invoice_lines)
        return invoice_lines

    @api.multi
    def _create_invoice_proprietario(self, proprietario, data_fatura=None):
        # verificando se existe linha marcada como repasse
        tem_repasse = False
        for line in self.recurring_invoice_line_ids:
            if line.repassa_prop:
                tem_repasse = True
        msg_erro = ''
        if not tem_repasse:
            return False, msg_erro
        """ GERANDO O CONTAS A PAGAR """
        invoice_vals = self._prepare_invoice_proprietario(proprietario, data_fatura)
        msg_erro = 'Erro para criar a fatura do Proprietario.'
        invoice = self.env['account.invoice'].create(invoice_vals)
        msg_erro = 'Erro para adicionar itens na fatura Proprietario.'
        self._prepare_order_lines_prop(self, invoice, proprietario)
        msg_erro = 'Erro pra confirmar a fatura Proprietario.'
        invoice.action_invoice_open()
        msg_erro = ''
        return invoice, msg_erro

    @api.model
    def cron_recurring_create_proprietario(self, data_next, data_fatura, venc_ini, venc_fim, id_ini):
        contracts = self.search(
            [('recurring_next_date', '<', data_next),
             ('recurring_invoices', '=', True),
             ('active','=',True),
             ('date_end', '>', venc_ini),
             ], order = 'name')
        #     ('id', '>', id_ini),
        #     ('id', '<', id_ini+3),
        contratos = []
        for ctr in contracts:
            contratos.append(ctr.name)
        #import pudb;pu.db
        inv = self.env['account.invoice'].search([
                    ('date_due', '>=', venc_ini),
                    ('date_due', '<=', venc_fim),
                    ('journal_id', '=', 2),
        ], order='origin')
        faturados = []
        for fatura in inv:
            faturados.append(str(fatura.origin)) 
        
        #import pudb;pu.db
        nao_faturado = list(set(contratos) - set(faturados))    
       
        contracts = self.search([
            ('name', 'in', nao_faturado)])
        for ctr in contracts[:50]:
            for prop in ctr.imovel_id.owner_ids:
                if prop.partner_id:
                    tempo = str(self.tempo(ctr.mes_contrato, ctr.ano_contrato))
                    data_f = datetime.strptime(data_fatura, '%Y-%m-%d')
                    reference = '%s(%s)-%s-%s' %(
                        ctr.name, tempo, 
                        str(data_f.month).zfill(2),
                        data_f.year)
                    # verifica se ja foi criado fatura pra este vencimento
                    inv = self.env['account.invoice'].search([
                    ('partner_id', '=', prop.partner_id.id),
                    ('date_invoice', '=', data_fatura),
                    ('reference', '=', reference),
                    ])
                    if not inv:
                        ctr._create_invoice_proprietario(prop, data_fatura)
        return True

    @api.model
    def cron_recurring_create_invoice(self):
        venc_ini = fields.date.today()
        # TODO 08/06/2022 acrescentei o venc_ini aqui verificar
        contracts = self.search(
            [('recurring_next_date', '<=', fields.date.today()),
             ('recurring_invoices', '=', True),
             ('date_end', '>', venc_ini),
             ('active','=',True)],limit=10)
        x = 0
        while x < len(contracts)+1:
            ctr = contracts[x:x+10]
            ctr.recurring_create_invoice()
            for contract in ctr:
                for prop in contract.imovel_id.owner_ids:
                    if prop.partner_id:
                        msg_prop = contract._create_invoice_proprietario(prop)
                        if msg_prop[1]:
                            ch_obj = self.env['mail.channel']
                            ch = ch_obj.sudo().search([('name', 'ilike', 'geral')])
                            ch.message_post(attachment_ids=[],body=msg_prop[1],content_subtype='html',
                                message_type='comment',partner_ids=[],subtype='mail.mt_comment',
                                email_from=self.env.user.partner_id.email,author_id=self.env.user.partner_id.id)

            x += 10
        return True
