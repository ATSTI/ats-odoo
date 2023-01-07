from odoo import models, fields, api
from odoo.tools.float_utils import float_round
import math


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def compute_discount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        discount = 0
        for line in self.invoice_line_ids:
            discount += (line.price_unit * line.quantity * line.discount) / 100
        self.discount = discount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign


    @api.one
    @api.depends('invoice_line_ids')
    def compute_total_before_discount(self):
        total = 0
        for line in self.invoice_line_ids:
            total += line.price
        self.total_before_discount = total

    discount_type = fields.Selection([('percentage', 'Porcentagem'), ('amount', 'Valor')], string='Tipo Desconto',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percentage')
    discount_rate = fields.Float(string='Desconto', digits=(16, 2),
                                 readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    #discount = fields.Monetary(string='Desconto', digits=(16, 2), default=0.0,
    #                           store=True, compute='compute_discount', track_visibility='always')
    total_before_discount = fields.Monetary(string='Total antes Desconto', digits=(16, 2), store=True, compute='compute_total_before_discount')

    def _calc_ratio(self, qty, total):
        if total > 0:
            return qty / total
        else:
            return 0

    @api.onchange('discount_type', 'discount_rate', 'invoice_lines_ids')
    def set_lines_discount(self):
        if self.discount_type == 'percentage' and self.discount_rate:
            total_desc = self.total_bruto * (self.discount_rate/100)
            total_desc = math.trunc(total_desc*100.0)/100.0
            total_linha = len(self.invoice_line_ids)
            for line in self.invoice_line_ids:
                # remover casas decimais do desconto
                tot = (line.quantity * line.price_unit)
                desc = tot * (self.discount_rate/100)
                desc = math.trunc(desc*100.0)/100.0
                if total_linha == 1:
                    desc = total_desc
                total_desc -= desc
                desc = desc / tot
                line.discount = desc*100
                total_linha -= 1
        else:
            total = discount = 0.0
            for line in self.invoice_line_ids:
                total += (line.quantity * line.price_unit)
            if self.discount_rate != 0:
                percentual = self._calc_ratio(self.discount_rate, total)
                discount = round(percentual * 100, 14)
            else:
                discount = self.discount_rate
            for line in self.invoice_line_ids:
                # remover casas decimais do desconto
                tot = (line.quantity * line.price_unit)
                desc = tot * (discount/100)
                desc = math.trunc(desc*100.0)/100.0
                desc = desc / tot
                line.discount = desc*100

    @api.multi
    def button_dummy(self):
        self.set_lines_discount()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('quantity', 'price_unit')
    def compute_line_price(self):
        self.price = self.quantity * self.price_unit

    #discount = fields.Float(string='Desconto (%)', digits=(16, 2), default=0.0)
    price = fields.Float(string='Price', digits=(16, 2), store=True, compute='compute_line_price')
