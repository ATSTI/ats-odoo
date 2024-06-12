# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    parcela_ids = fields.One2many(
        'invoice.parcela', 'move_id',
        string=u"Parcelas")
    num_parcela = fields.Integer('Núm. Parcela')
    dia_vcto = fields.Integer('Dia Vencimento', default=0)
    vlr_prim_prc = fields.Float('Valor Prim. Parcela', default=0.0)
    payment_mode_id = fields.Many2one(
       'account.payment.mode', string=u"Modo de pagamento")
    
    # TODO saindo o mesmo nome para todas as parcelas
   
    def calcular_vencimento(self, dia_preferencia, parcela):
        hj = date.today()
        dia = hj.day
        if dia_preferencia:
            if dia_preferencia <= dia:
                parcela += 1
            dia = dia_preferencia
        data_vcto = hj + relativedelta(day=dia,months=parcela)
        return data_vcto

    @api.depends('num_parcela', 'dia_vcto', 'vlr_prim_prc')
    def action_calcula_parcela(self):
        self.parcela_ids = False
        self._recompute_payment_terms_lines()
        prcs = []       
        prc = 0
        # if self.rateio_frete:
        total = self.amount_total
        #else:
        #    total = self.amount_total - self.amount_freight_value
        valor_prc = 0.0
        if self.vlr_prim_prc:
            total = self.currency_id.round(total - self.vlr_prim_prc)
            if self.num_parcela > 1:
                valor_prc = self.currency_id.round(total / (self.num_parcela - 1))
            else:
                if self.num_parcela > 1:
                    valor_prc = self.currency_id.round(total / (self.num_parcela - 1))
                else:
                    valor_prc = self.currency_id.round(total)
        else:
            if self.num_parcela > 0:
                valor_prc = self.currency_id.round(total / self.num_parcela)
            else:
                valor_prc = self.currency_id.round(total)
        valor_parc = valor_prc
        while (prc < self.num_parcela):
            data_parc = self.calcular_vencimento(self.dia_vcto,prc)
            if prc == 0 and self.vlr_prim_prc > 0.0:
                valor_parc = self.currency_id.round(self.vlr_prim_prc)
            if prc == 0 and self.vlr_prim_prc == 0.0:
                total -= valor_parc
            elif prc > 0:
                total -= valor_parc
            if (self.num_parcela - prc) == 1:
                if total > 0.0 or total < 0.0:
                    valor_parc = self.currency_id.round(valor_parc + total)
            #if not self.rateio_frete and prc == 0:
            #    valor_parc = valor_parc + self.amount_freight_value
            prcs.append((0, None, {
                'currency_id': self.currency_id.id,
                'data_vencimento': data_parc,
                'valor': self.currency_id.round(valor_parc),
                'numero_fatura': str(prc+1).zfill(2),
                'payment_mode_id': self.payment_mode_id.id,
            }))
            valor_parc = valor_prc
            prc += 1
        if prcs:
            # import pudb;pu.db
            if self.parcela_ids:
                self.parcela_ids.unlink()
            self.parcela_ids = prcs
            self._recompute_payment_terms_lines()

    @api.onchange('num_parcela', 'dia_vcto', 'vlr_prim_prc')
    def _onchange_recompute_parcelas(self):
        if self.parcela_ids:
            # import pudb;pu.db
            self.parcela_ids = False

    # @api.onchange('parcela_ids')
    # def _onchange_parcela_ids(self):
    #     import pudb;pu.db
    #     if self.parcela_ids._origin:
    #         self._recompute_payment_terms_lines()

    def _recompute_payment_terms_lines(self):
        import pudb;pu.db
        self.ensure_one()
        self = self.with_company(self.company_id)
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_company(self.journal_id.company_id)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            if payment_terms_lines:
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    return self.partner_id.property_account_receivable_id
                else:
                    return self.partner_id.property_account_payable_id
            else:
                # Search new account.
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                    ('deprecated', '=', False),
                ]
                return self.env['account.account'].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id and not self.num_parcela:
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.company_id.currency_id)
                if not self.num_parcela and self.currency_id == self.company_id.currency_id:
                    # Single-currency.
                    return [(b[0], b[1], b[1]) for b in to_compute]
                else:                      
                    # Multi-currencies.
                    to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date, currency=self.currency_id)
                    return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
            elif self.num_parcela:
                lista_parcelas = []
                if self.parcela_ids:
                    for prc in self.parcela_ids:
                        lista_parcelas.append((
                            prc.data_vencimento.strftime("%Y-%m-%d"),
                            -(prc.valor), 
                            -(prc.valor)
                        ))
                else:
                    # quando duplica o parcela_ids nao esta vindo
                    for prc in self.financial_move_line_ids:
                        lista_parcelas.append((
                            prc.date_maturity.strftime("%Y-%m-%d"),
                            -(prc.debit), 
                            -(prc.debit)
                        ))
                return lista_parcelas
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        """ Creates invoice related analytics and financial move lines """
        # account_move = self.env['account.move']
        
        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0
            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:        
                currency = self.journal_id.company_id.currency_id
                if currency and currency.is_zero(balance) and len(to_compute) > 1:
                    continue
                
                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                    candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })
                new_terms_lines += candidate
                if in_draft_mode:
                    candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
            return new_terms_lines
        
        existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity
                                                                                                                                                              
    # def finalize_invoice_move_lines(self, move_lines):
    #     res = super(AccountMove, self).\
    #     finalize_invoice_move_lines(move_lines)
    #     parcela = 1
    #     for line in move_lines:
    #         if 'name' in line[2]:
    #             for inv in self:
    #                 if inv.parcela_ids:
    #                     pm = inv.parcela_ids[parcela-1].payment_mode_id.id
    #                     parc = str(parcela).zfill(2)
    #                     if line[2]['name'] == parc:
    #                         line[2]['payment_mode_id'] = pm
    #                         parcela += 1
    #     return res


class InvoiceParcela(models.Model):
    _name = 'invoice.parcela'
    _order = 'data_vencimento'

    move_id = fields.Many2one('account.move', string="Fatura")
    currency_id = fields.Many2one(
        'res.currency', related='move_id.currency_id',
        string="EDoc Currency", readonly=True)
    numero_fatura = fields.Char(string=u"Número Fatura", size=60)
    data_vencimento = fields.Date(string="Data Vencimento")
    valor = fields.Monetary(string="Valor Parcela")
    payment_mode_id = fields.Many2one(
       'account.payment.mode', string=u"Modo de pagamento")
