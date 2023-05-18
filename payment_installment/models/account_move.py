# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    parcela_ids = fields.One2many(
        'invoice.parcela', 'move_id',
        string=u"Parcelas")
    num_parcela = fields.Integer('Núm. Parcela')
    dia_vcto = fields.Integer('Dia Vencimento', default=0)
    rateio_frete = fields.Boolean('Rateio do Frete', default=False)
    vlr_prim_prc = fields.Float('Valor Prim. Parcela', default=0.0)
    payment_mode_id = fields.Many2one(
       'account.payment.mode', string=u"Modo de pagamento")
    
    def action_post(self):
        different = False
        for prc in self.parcela_ids:
            fin = self.financial_move_line_ids.filtered(lambda l: l.date_maturity == prc.data_vencimento)
            if fin.debit != prc.valor:
                different = True
                break
        if different:
            raise UserError(_(f"Parcela não foi confirmada, favor confirmar na aba PARCELAS."))       
        return super().action_post()

    def action_confirma_parcela(self): 
        if self.num_parcela > 0:
            parcela = 0
            for fin in self.financial_move_line_ids:
                parc = self.parcela_ids[parcela]
                fin.with_context(check_move_validity=False).update({
                        'date_maturity': parc.data_vencimento,
                        'amount_currency': parc.valor,
                        'debit': parc.valor,
                        'balance': parc.valor,
                        'credit': 0.0,
                    })
                parcela += 1
                account = fin.account_id
            for prc in self.parcela_ids[parcela:]:
                create_method = self.env['account.move.line'].with_context(check_move_validity=False).create
                candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': prc.valor,
                        'balance': prc.valor,
                        'credit': 0.0,
                        'quantity': 1.0,
                        'amount_currency': prc.valor,
                        'date_maturity': prc.data_vencimento,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })

    def calcular_vencimento(self, dia_preferencia, parcela):
        if self.invoice_date:
            hj = self.invoice_date
        else:
            hj = date.today()
        dia = hj.day
        mes = hj.month
        ano = hj.year
        if dia_preferencia:
            if dia >= dia_preferencia:
                mes = mes + 1
                if mes > 12:
                    mes = 1
                    ano = ano + 1            
            dia = dia_preferencia
        mes = mes + parcela

        if mes > 12 and mes < 25:
            mes = mes - 12
            ano = ano + 1
        if mes > 24 and mes < 37:
            mes = mes - 24
            ano = ano + 2
        if mes > 36 and mes < 49:
            mes = mes - 36
            ano = ano + 3
        if mes > 48 and mes < 61:
            mes = mes - 48
            ano = ano + 4
        if mes > 60 and mes < 73:
            mes = mes - 60
            ano = ano + 5
        if mes > 72 and mes < 85:
            mes = mes - 72
            ano = ano + 6
        if mes > 84 and mes < 97:
            mes = mes - 84
            ano = ano + 7
        if mes > 96 and mes < 109:
            mes = mes - 96
            ano = ano + 8
        if mes > 108 and mes < 121:
            mes = mes - 108
            ano = ano + 9
        
        if dia > 28 and mes == 2:
            dia = 28
        if dia == 31 and mes not in (1,3,5,7,8,10,12):
            dia = 30
        data_str = '%s-%s-%s' %(ano, mes, dia)
        data_vcto = datetime.strptime(data_str,'%Y-%m-%d').date()
        return data_vcto

    @api.depends('num_parcela', 'dia_vcto', 'vlr_prim_prc')
    def action_calcula_parcela(self):
        prcs = []       
        prc = 0
        if self.rateio_frete:
            total = self.amount_total
        else:
            total = self.amount_total - self.amount_freight_value
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
            if not self.rateio_frete and prc == 0:
                valor_parc = valor_parc + self.amount_freight_value
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
            if self.parcela_ids:
                self.parcela_ids.unlink()
            self.parcela_ids = prcs
                
    
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.invoice_date:
                inv.with_context(ctx).write({'invoice_date': fields.Date.context_today(self)})
            date_due = inv.invoice_date
            if inv.parcela_ids:
                for prc in inv.parcela_ids:
                     date_due= prc.data_vencimento
                     break
            if not inv.date_due:
                inv.with_context(ctx).write({'date_due': date_due})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'

            if inv.parcela_ids:
                for prc in inv.parcela_ids:
                    if total < 0:
                        prc.valor = prc.valor*(-1)
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': prc.valor,
                        'account_id': inv.account_id.id,
                        'payment_mode_id': prc.payment_mode_id.id,
                        'date_maturity': prc.data_vencimento,
                        'amount_currency': prc.valor,
                        'currency_id': inv.currency_id.id,
                        'move_id': inv.id
                    })
                    prc.valor = prc.valor*(-1)
                    
            elif inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.invoice_date)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv.date or inv.invoice_date
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'payment_mode_id': inv.payment_mode_id.id,
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'move_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'move_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.invoice_date
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True    
                                                                                                                                                              
    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountMove, self).\
        finalize_invoice_move_lines(move_lines)
        parcela = 1
        for line in move_lines:
            if 'name' in line[2]:
                for inv in self:
                    if inv.parcela_ids:
                        pm = inv.parcela_ids[parcela-1].payment_mode_id.id
                        parc = str(parcela).zfill(2)
                        if line[2]['name'] == parc:
                            line[2]['payment_mode_id'] = pm
                            parcela += 1
        return res

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
