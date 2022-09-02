# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class ExecuteRenegotiate(models.TransientModel):

    _name = "execute.renegotiate"
    _description = "Executar renegociação"

    @api.onchange('juro', 'multa')
    def _onchange_incluir_juros(self):
        self.calcula_juros()

    @api.depends('valor')
    def compute_total(self):
        self.calcula_juros()

    def calcula_juros(self):
        aml_obj = self.env['account.invoice']
        context = dict(self._context or {})
        amount = 0.0
        juro = 0.0
        multa = 0.0
        juro_dia = (self.juro / 100) / 30
        multa_dia = (self.multa / 100)
        hj = date.today()
        dias_atraso = 0
        for fat in aml_obj.browse(context.get('active_ids')):
            amount += fat.residual
            dif = hj - fat.date_due
            if dias_atraso < dif.days:
                dias_atraso = dif.days
            if dif.days > 0:
                juro += fat.residual * dif.days * juro_dia
                multa += fat.residual * multa_dia
        self.valor = amount
        self.valor_juro = juro
        self.valor_multa = multa
        self.valor_total = amount + juro + multa
        self.numero_parcela = dias_atraso

    primeiro_vencimento = fields.Date('Último vencimento')
    numero_parcela = fields.Integer('Número parcela')
    valor_total = fields.Float(string="Valor Total", compute="compute_total")
    juro = fields.Float(string="Juro Mês", default=1.0)
    multa = fields.Float(string="Multa", default=2.0)
    cobrar_juros = fields.Boolean(string="Cobrar juros ?")
    valor_multa = fields.Float(string="Valor Multa")
    valor_juro = fields.Float(string="Valor Juro")
    valor = fields.Float(string="Valor Negociado")

    def execute_faturamento(self):
        if not self.data_faturar:
            raise UserError(_("Porfavor prencher campo Data inicial."))
        domain = []
        if self.data_faturar:
            domain += [('recurring_next_date', '>=', self.data_faturar),
                ('recurring_invoices', '=', True),
                ('state', '=', 'done'),
                ('active','=',True)]      
        order_ids = self.env['contract.contract'].search(domain)
        for ctr in order_ids:
            ctr.recurring_create_invoice(ctr)

    def calcula_total(self):
        if not self.data_faturar:
            raise UserError(_("Por favor prencher campo Data inicial."))
        domain = []
        if self.data_faturar:
            domain += [('recurring_next_date', '>=', self.data_faturar),
                ('recurring_invoices', '=', True),
                ('state', '=', 'done'),
                ('active','=',True)]      
        order_ids = self.env['contract.contract'].search(domain)
        for ctr in order_ids:
            ctr.recurring_create_invoice(ctr)

    def action_confirm_renegotiate(self):       
        account_invoice = self.env['account.invoice']
        context = dict(self._context or {})
        diario = self.env['account.journal'].search([('name', 'ilike', 'acordo')])
        account = self.env['account.account'].search([('name', 'ilike', 'c-acordo')])
        account_p = self.env['account.account'].search([('name', 'ilike', 'p-acordo')])
        iml = []
        nfe = 0
        desc = ''
        faturas = account_invoice.browse(context.get('active_ids'))
        juro_fat = self.valor_juro + self.valor_multa
        if juro_fat:
            juro_fat = juro_fat / self.valor
        for fat in faturas:
            # account_id = fat.account_id.id
            partner_id = fat.partner_id.id
            journal_id = diario.id
            total = fat.residual
            if self.cobrar_juros and (
                self.valor_juro or self.valor_multa
            ):
                total += total * juro_fat
            iml += [(0, 0, {
                'name': fat.number,
                'quantity': 1.0,
                'account_id': account_p.id,
                'price_unit': round(total,2),
            })]
            if desc:
                desc += ', '
            if fat.origin:
                desc += fat.origin
            nfe = fat.nfe_number

        move_vals = {
            'origin': 'Acordo ' + desc,
            'journal_id': journal_id,
            'date': date.today(),
            'nfe_number': nfe,
            'partner_id': partner_id,
            'account_id': account.id,
        }
        move_vals['date_due'] = self.primeiro_vencimento
        move = account_invoice.create(move_vals)
        move.write({'invoice_line_ids': iml})

        self.baixa_pagamentos(faturas[0], diario, "", self.valor_total-self.valor_juro-self.valor_multa, "", 0.0)

    def baixa_pagamentos(self, move_line_id, journal_id, caixa, valor, cod_forma, juros):
        bank = self.env['res.partner.bank'].search([])
        invoices = move_line_id
        baixar_tudo = 'reconcile'
        bank_account = invoices.partner_bank_id or bank[0]
        payment_type = 'inbound'
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
        move_line = invoices[0].receivable_move_line_ids[0]
        for line in invoices[0].receivable_move_line_ids:
            if not line.reconciled:
                move_line = line
        vals = {
            'journal_id': journal_id.id,
            'payment_method_id': payment_method_id.id,
            'payment_date': datetime.now(),
            'communication': invoices.name,
            'move_line_id': move_line.id,
            'payment_type': payment_type,
            'amount': valor+juros,
            'currency_id': journal_id.company_id.currency_id.id,
            'partner_id': move_line_id.partner_id.id,
            'partner_type': 'customer',
            'partner_bank_account_id': bank_account.id,
            'multi': False,
            'payment_difference_handling': baixar_tudo,
            'writeoff_account_id': conta_juros,
            'writeoff_label': juros_desc,
            'account_id': move_line_id.account_id.id,
        }   
        payment = self.env['account.payment']
        pay = payment.with_context(
            force_counterpart_account=move_line_id.account_id.id).\
            create(vals)
        pay.post()