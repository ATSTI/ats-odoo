# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    parcela_ids = fields.One2many(
        'invoice.parcela', 'move_id',
        string=u"Parcelas", copy=False)
    num_parcela = fields.Integer('Núm. Parcela')
    dia_vcto = fields.Integer('Dia Vencimento', default=0)
    rateio_frete = fields.Boolean('Rateio do Frete', default=False)
    vlr_prim_prc = fields.Float('Valor Prim. Parcela', default=0.0)
    payment_mode_install_id = fields.Many2one(
        'account.payment.mode', string=u"Modo de pagamento")
    
    # TODO saindo o mesmo nome para todas as parcelas
    def action_post(self):
        different = False
        for prc in self.parcela_ids:
            fin = self.due_line_ids.filtered(lambda l: l.date_maturity == prc.data_vencimento)
            if len(fin) > 1:
                raise UserError(_(f"Existe mais de uma parcela com o mesmo vencimento, faça a correção."))
            if self.move_type == "in_invoice":
                if fin.credit != prc.valor:
                    different = True
                    break
            if self.move_type == "out_invoice":
                if fin.debit != prc.valor:
                    different = True
                    break
        if different:
            raise UserError(_(f"Parcela não foi confirmada, favor confirmar na aba PARCELAS."))
        res = super().action_post()
        for line in self.due_line_ids:
            if line.move_id.document_type_id:
                nome_parcela = line.move_id.document_number
            else:
                nome_parcela = line.move_id.name
            if line.name and not nome_parcela in line.name:
                line.name = f"{nome_parcela}-{line.name}"
            else:
                line.name = nome_parcela
        # TODO quando confirma a primeira vez esta excluindo as parcelas
        # rotina abaixo pra evitar isso, rever
        # if len(self.due_line_ids) < len(self.parcela_ids):
        #     self.button_draft()
        #     self.action_confirma_parcela()
        #     res = super().action_post()
        return res

    def action_confirma_parcela(self):
        valor_total = 0
        for prc in self.parcela_ids:
            valor_total += prc.valor
        if round(self.amount_total, 2) != round(valor_total, 2):
            raise UserError(_(f"Valor da soma das parcelas: {str(valor_total)}, diferente do valor total: {str(self.amount_total)}.")) 
        if self.num_parcela > 0:
            date_due = False
            parcelas = []
            for prc in self.parcela_ids:
                # a data de vencimento da fatura sera o ultimo vencimento
                date_due = prc.data_vencimento
            if date_due:
                self.update({'invoice_date_due': date_due})
            sign = 1                
            for prc in self.parcela_ids:
                valor_cre = 0
                valor_deb = 0
                if self.move_type == "in_invoice":
                    valor_cre = prc.valor
                if self.move_type == "out_invoice":
                    valor_deb = prc.valor    
                for line in self.line_ids:
                    if line.account_type in ('asset_receivable', 'liability_payable'):
                        sign = 1 if line.balance > 0.0 else -1
                        conta_lancamento = line.account_id
                        line.with_context(check_move_validity=False, dynamic_unlink=True).unlink()
                create_method = {
                        'name': prc.numero_fatura,
                        'debit': valor_deb if valor_deb else 0.0,
                        'credit': -valor_cre if valor_cre else 0.0,
                        'balance': valor_deb if valor_deb else -valor_cre,
                        'quantity': 1.0,
                        'amount_currency': sign * prc.valor,
                        'date_maturity': prc.data_vencimento,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': conta_lancamento.id,
                        'partner_id': self.commercial_partner_id.id,
                        'payment_mode_id': prc.payment_mode_id.id or self.payment_mode_id.id or False,
                }
                parcelas.append(create_method)
            self.env['account.move.line'].with_context(check_move_validity=False,dynamic_unlink=True).create(parcelas)
   
    def calcular_vencimento(self, dia_preferencia, parcela):
        if self.invoice_date:
            hj = self.invoice_date
        else:
            hj = date.today()
        dia = hj.day
        # calcula a data de vencimento  
        if dia_preferencia:
            if dia >= dia_preferencia:
                parcela += 1
            dia = dia_preferencia
        else:
            parcela += 1
        year = divmod(hj.month+parcela - 1, 12)[0] + hj.year
        next_month = (hj.month + parcela) % 12 or 12
        if next_month == 2 and dia > 28:
            dia = 28
        if dia == 31 and next_month not in (1,3,5,7,8,10,12):
            dia = 30
        data_vcto = datetime(year, next_month, dia)
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
                'payment_mode_id': self.payment_mode_install_id.id,
            }))
            valor_parc = valor_prc
            prc += 1
        if prcs:
            if self.parcela_ids:
                self.parcela_ids.unlink()
            self.parcela_ids = prcs


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # substitui o metodo deste modulo bank-payment/account_payment_partner
    # porque nao permite ao usuario mudar a forma de pagamento
    # de uma unica parcela
    @api.depends("move_id", "move_id.payment_mode_id")
    def _compute_payment_mode(self):
        if self.move_id.parcela_ids:
            return
        else:
            return super()._compute_payment_mode()

class InvoiceParcela(models.Model):
    _name = 'invoice.parcela'
    _order = 'data_vencimento'
    _description = "Parcelas da Fatura"

    name = fields.Char(string="Descrição", size=30) 
    move_id = fields.Many2one('account.move', string="Fatura")
    currency_id = fields.Many2one(
        'res.currency', related='move_id.currency_id',
        string="EDoc Currency", readonly=True)
    numero_fatura = fields.Char(string=u"Número Fatura", size=60)
    data_vencimento = fields.Date(string="Data Vencimento")
    valor = fields.Monetary(string="Valor Parcela")
    payment_mode_id = fields.Many2one(
       'account.payment.mode', string=u"Modo de pagamento")
