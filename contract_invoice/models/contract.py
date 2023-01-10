# -*- coding: utf-8 -*-
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from datetime import date


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends('recurring_invoice_line_ids.price_subtotal')
    def _amount_total(self):
        for order in self:
            soma = 0.0
            for line in order.recurring_invoice_line_ids:
                soma += (line.price_subtotal)
            order.amount_total = soma

    payment_mode_id = fields.Many2one(
        'l10n_br.payment.mode',
        string='Forma Pagamento'
        )
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Dia Vencimento'
        )
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position',
        string=u"Posição Fiscal"
        )
    #invoice_partner_id = fields.Many2one('res.partner', string='Cliente faturamento'

    amount_total = fields.Float(compute='_amount_total', 
        string="Valor total", digits=dp.get_precision('Product Price'), store=True)
        
    msg_faturamento = fields.Char(u'Mensagem Faturamento')
    envia_email = fields.Boolean(string='Envia por Email')
    
    @api.one
    @api.depends('date_start')
    def _compute_vencimento(self):
        #import pudb;pu.db
        self.mes_contrato = self.date_start.month
        self.ano_contrato = self.date_start.year
    
    mes_contrato = fields.Integer(string='Mes Contrato',
        store=True, readonly=True, compute='_compute_vencimento')
    ano_contrato = fields.Integer(string='Ano Contrato',
        store=True, readonly=True, compute='_compute_vencimento')    

    def tempo(self, mes, ano):
        #import pudb;pu.db
        dt = date.today()
        mes_atual = dt.month
        ano_atual = dt.year
        #soma_mes = 0
        #if mes < mes_atual:
        #    ano_atual -= 1
        #    soma_mes = mes - mes_atual
        #else:
        #    soma_mes = mes_atual - mes
        #tempo = ((ano_atual - ano) * 12) + soma_mes
        if mes > mes_atual:
            tempo = abs(ano_atual - ano) * 12 - abs(mes_atual - mes)
        else:
            tempo = abs(ano_atual - ano) * 12 + abs(mes_atual - mes)

        return str(tempo).zfill(2)

    #@api.onchange('partner_id')
    #def _onchange_partner_id(self):
    #    if self.partner_id and self.partner_id.property_payment_term_id:
    #        self.payment_term_id = self.partner_id.property_payment_term_id.id
    #    if self.partner_id and self.partner_id.property_account_position_id:
    #        self.fiscal_position_id = self.partner_id.property_account_position_id.id
    #    if self.partner_id:
    #        if self.partner_id.legal_name:
    #            self.name = self.partner_id.legal_name
    #        else:
    #            self.name = self.partner_id.name

    @api.model
    def _prepare_invoice(self):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice()
        if self.payment_mode_id:
            invoice_vals['payment_mode_id'] = self.payment_mode_id.id
            #invoice_vals['partner_bank_id'] = (
            #    contract.partner_id.bank_ids[:1].id or
            #    contract.payment_mode_id.bank_id.id)
        if self.payment_term_id:
            invoice_vals['payment_term_id'] = self.payment_term_id.id
        if self.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = self.fiscal_position_id.id
        invoice_vals['contract_id'] = self.id
        today = date.today()
        tempo = self.tempo(self.mes_contrato, self.ano_contrato)
        invoice_vals['reference'] = '%s(%s)-%s-%s' %(
            self.name, tempo, str(today.month).zfill(2), today.year)
        invoice_vals['type'] = 'out_invoice'
        return invoice_vals

    """ nao preciso disso no cadastro do cliente
    @api.multi
    def write(self, values):
        vals = {}
        if 'payment_term_id' in values:
            vals['property_payment_term_id'] = values.get('payment_term_id')
        if 'payment_mode_id' in values:
            vals['payment_mode_id'] = values.get('payment_mode_id')
        if 'fiscal_position_id' in values:
            vals['property_account_position_id'] = values.get('fiscal_position_id')
        if vals:
            partner = self.env['res.partner'].browse([self.partner_id.id])
            partner.write(vals)
        return super(AccountAnalyticAccount, self).write(values);


    @api.model
    def create(self, values):
        vals = {}
        if 'payment_term_id' in values:
            vals['property_payment_term_id'] = values.get('payment_term_id')
        if 'payment_mode_id' in values:
            vals['payment_mode_id'] = values.get('payment_mode_id')
        if 'fiscal_position_id' in values:
            vals['property_account_position_id'] = values.get('fiscal_position_id')
        if vals:
            partner = self.env['res.partner'].browse([values.get('partner_id')])
            partner.write(vals)
        return super(AccountAnalyticAccount, self).create(values);
    """

class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    date_start = fields.Date(string='Data inicio')
    date_stop = fields.Date(string='Data Fim')
