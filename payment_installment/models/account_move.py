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
    # payment_mode_id = fields.Many2one(
    #    'account.payment.mode', string=u"Modo de pagamento")
    

    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     move = super().copy(default)
    #     import pudb;pu.db
    #     if move.is_invoice(include_receipts=True):
    #         if move.parcela_ids:
    #             move.action_confirma_parcela()
    #     return super().copy(default)

    # TODO saindo o mesmo nome para todas as parcelas
    def action_post(self):
        different = False
        for prc in self.parcela_ids:
            fin = self.financial_move_line_ids.filtered(lambda l: l.date_maturity == prc.data_vencimento)
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
        # TODO quando confirma a primeira vez esta excluindo as parcelas
        # rotina abaixo pra evitar isso, rever
        if len(self.financial_move_line_ids) < len(self.parcela_ids):
            self.button_draft()
            self.action_confirma_parcela()
            res = super().action_post()
        # correcao name parcela
        # for prc in self.parcela_ids:
        #     fin = self.financial_move_line_ids.filtered(lambda l: l.date_maturity == prc.data_vencimento)
        #     if fin.name and fin.name.find('-') < 0:
        #         fin.write({'name': f"{self.name}-{fin.name}"})

        return res

    def action_confirma_parcela(self):
        valor_total = 0
        for prc in self.parcela_ids:
            valor_total += prc.valor
        if round(self.amount_total, 2) != round(valor_total, 2):
            raise UserError(_(f"Valor da soma das parcelas: {str(valor_total)}, diferente do valor total: {str(self.amount_total)}.")) 
        if self.num_parcela > 0:
            account = self.financial_move_line_ids[0].account_id
            self.financial_move_line_ids.with_context(check_move_validity=False).unlink()
            date_due = False
            for prc in self.parcela_ids:
                create_method = self.env['account.move.line'].with_context(check_move_validity=False).create
                valor_cre = 0
                valor_deb = 0
                if self.move_type == "in_invoice":
                    valor_cre = prc.valor
                if self.move_type == "out_invoice":
                    valor_deb = prc.valor
                create_method({
                        'name': prc.numero_fatura,
                        'debit': valor_deb,
                        'balance': prc.valor,
                        'credit': valor_cre,
                        'quantity': 1.0,
                        'amount_currency': prc.valor,
                        'date_maturity': prc.data_vencimento,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                        'payment_mode_id': prc.payment_mode_id.id or self.payment_mode_id.id,
                })
                date_due = prc.data_vencimento
                # self.payment_reference = "01"
            if date_due:
                self.invoice_date_due = date_due
   
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
                # mes = mes + 1
                # if mes > 12:
                #     mes = 1
                #     ano = ano + 1
                parcela += 1
            dia = dia_preferencia
        else:
            parcela += 1
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

    # def copy(self, default=None):
    #     return super(AccountMove, self.with_context(duplicando_fatura=True)).copy(default)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # substitui o metodo deste modulo bank-payment/account_payment_partner
    # porque nao permite ao usuario mudar a forma de pagamento
    # de uma unica parcela
    @api.depends("move_id", "move_id.payment_mode_id")
    def _compute_payment_mode(self):
        for line in self:
            if line.move_id.parcela_ids:
                line.payment_mode_id = False
            else:
                super(AccountMoveLine, line)._compute_payment_mode()

    # @api.model_create_multi
    # def create(self, vals_list):
    #     if self.env.context.get('skip_debit_merge'):
    #         return super().create(vals_list)

    #     res = super().create(vals_list)

    #     if not self.env.context.get('duplicando_fatura'):
    #         return res

    #     for move in res.mapped('move_id'):
    #         if move.state != 'draft':
    #             continue
    #         debit_lines = move.line_ids.filtered(lambda l: l.debit > 0 and not l.display_type)
    #         credit_lines = move.line_ids.filtered(lambda l: l.credit > 0 and not l.display_type)

    #         if not debit_lines or not credit_lines:
    #             continue

    #         total_debit = sum(debit_lines.mapped('debit'))
    #         account_id = debit_lines[0].account_id.id

    #         commands = []

    #         for line in debit_lines:
    #             commands.append((2, line.id))

    #         commands.append((0, 0, {
    #             'name': 'Débito unificado (CALCULE NOVAMENTE AS PARCELAS)',
    #             'debit': total_debit,
    #             'credit': 0.0,
    #             'balance': total_debit,
    #             'amount_currency': total_debit,
    #             'account_id': account_id,
    #             'currency_id': move.currency_id.id,
    #             'partner_id': move.partner_id.id,
    #             'display_type': False,
    #         }))

    #         with self.env.norecompute():
    #             move.with_context(
    #                 check_move_validity=False,
    #                 skip_debit_merge=True
    #             ).write({'line_ids': commands})
    #         move._recompute_dynamic_lines()


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
