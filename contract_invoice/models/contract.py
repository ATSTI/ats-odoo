# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression
# import odoo.addons.decimal_precision as dp
from datetime import date


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    # @api.depends('recurring_invoice_line_ids.price_subtotal')
    # def _amount_total(self):
    #     for order in self:
    #         soma = 0.0
    #         for line in order.recurring_invoice_line_ids:
    #             soma += (line.price_subtotal)
    #         order.amount_total = soma

    # payment_mode_id = fields.Many2one(
    #     'l10n_br.payment.mode',
    #     string='Forma Pagamento'
    #     )
    # payment_term_id = fields.Many2one(
    #     'account.payment.term',
    #     string='Dia Vencimento'
    #     )
    # fiscal_position_id = fields.Many2one(
    #     'account.fiscal.position',
    #     string=u"Posição Fiscal"
    #     )
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Forma Pagamento"
    )        

    # payment_mode_id = fields.Integer(
    #     string='Forma Pagamento'
    #     )
    # payment_term_id = fields.Integer(
    #     string='Dia Vencimento'
    #     )
    # fiscal_position_id = fields.Integer(
    #     string=u"Posição Fiscal"
    #     )


    #invoice_partner_id = fields.Many2one('res.partner', string='Cliente faturamento'

    # amount_total = fields.Float(compute='_amount_total', 
    #     string="Valor total", digits=dp.get_precision('Product Price'), store=True)
        
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
    def _prepare_invoice(self, date_invoice, journal=None ):
        #journal = self.env["account.journal"].browse([1])
        vals = super(ContractContract, self).\
            _prepare_invoice(date_invoice)
        for invoice_vals in vals:
            if not isinstance(invoice_vals, dict):
                continue
            if self.payment_mode_id:
                invoice_vals['payment_mode_id'] = self.payment_mode_id.id
                if self.payment_mode_id.payment_mode_domain:
                    if self.payment_mode_id.payment_mode_domain == "boleto":
                        if self.payment_mode_id.fixed_journal_id:
                            if self.payment_mode_id.fixed_journal_id.bank_id.code_bc == "077":
                                invoice_vals["partner_bank_id"] = self.payment_mode_id.fixed_journal_id.bank_account_id.id
            #invoice_vals['partner_bank_id'] = (
            #    contract.partner_id.bank_ids[:1].id or
            #    contract.payment_mode_id.bank_id.id)
            if self.payment_term_id:
                invoice_vals['invoice_payment_term_id'] = self.payment_term_id.id
            if self.fiscal_position_id:
               invoice_vals['fiscal_position_id'] = self.fiscal_position_id.id
            today = date.today()
            tempo = self.tempo(self.mes_contrato, self.ano_contrato)
            if tempo == "0":
                tempo = str(self.id)
            invoice_vals['ref'] = '%s(%s)-%s-%s' %(
                self.name, tempo, str(today.month).zfill(2), today.year)
            #invoice_vals['move_type'] = 'out_invoice'
            if not invoice_vals['partner_id']:
                invoice_vals['partner_id'] = self.partner_id.id 
        return vals

    @api.model
    def _cron_recurring_create(self, date_ref=False, create_type="invoice"):
        """
        The cron function in order to create recurrent documents
        from contracts.
        """
        _recurring_create_func = self._get_recurring_create_func(
            create_type=create_type
        )
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = self._get_contracts_to_invoice_domain(date_ref)
        domain = expression.AND(
            [
                domain,
                [("generation_type", "=", create_type)],
            ]
        )
        contracts = self.search(domain)
        companies = set(contracts.mapped("company_id"))
        # Invoice by companies, so assignation emails get correct context
        for company in companies:
            contracts_to_invoice = contracts.filtered(
                lambda c: c.company_id == company
                and (not c.date_end or c.recurring_next_date <= c.date_end)
            ).with_company(company)
            _recurring_create_func(contracts_to_invoice[:10], date_ref)
        return True

# class AccountAnalyticInvoiceLine(models.Model):
#     _inherit = 'account.analytic.invoice.line'

#     date_start = fields.Date(string='Data inicio')
#     date_stop = fields.Date(string='Data Fim')
