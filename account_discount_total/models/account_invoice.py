# -*- coding: utf-8 -*-

from locale import currency
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_type = fields.Selection([
        ('percent', 'Percentagem'), ('amount', 'Valor')], 
        string='Tipo desconto',
        readonly=True, 
        states={'draft': [('readonly', False)]}, 
        default='percent'
    )
    discount_rate = fields.Float('Total desconto', 
        digits=(16, 2), 
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    @api.model_create_multi
    def create(self, vals_list):
        results = super(AccountMove, self).create(vals_list)
        for values, inv in zip(vals_list, results):
            discount_type = values.get('discount_type')
            discount_rate = values.get('discount_rate')
            if discount_type and discount_rate:
                inv.discount_type = discount_type
                inv.discount_rate = discount_rate
        return results

    def button_dummy(self):
        for inv in self:
            inv._compute_discounts()
        return True

    @api.depends('discount_type', 'discount_rate', 'invoice_line_ids.price_subtotal')
    def _compute_discounts(self):
        for inv in self:
            currency = inv.currency_id or self.env.company.currency_id
            total = sum(line.quantity * line.price_unit for line in inv.invoice_line_ids)

            # Se não existe desconto configurado
            if not inv.discount_type or not inv.discount_rate or total == 0:
                inv.amount_price_gross = currency.round(total)
                inv.amount_discount_value = 0.0
                inv.amount_untaxed = total
                inv.amount_total = total
                for line in inv.invoice_line_ids:
                    line.discount_value = 0.0
                    line.discount = 0.0
                continue

            # -------- Cálculo do desconto ----------
            if inv.discount_type == 'percent':
                discount_value_total = currency.round((inv.discount_rate / 100.0) * total)

            elif inv.discount_type == 'amount':   # valor fixo
                discount_value_total = currency.round(min(inv.discount_rate, total))  # evita desconto maior que o total

            else:
                discount_value_total = 0.0

            # -------- Distribuição do desconto entre as linhas ----------
            # proporcional ao valor da linha
            soma_descontos = 0.0
            base_lines = inv.invoice_line_ids.filtered(lambda line: line.display_type == 'product')

            for line in base_lines:
                proporcao = (discount_value_total / total) if total else 0
                desconto_linha = currency.round(line.price_subtotal * proporcao)
                line.discount_value = desconto_linha
                soma_descontos += desconto_linha

            # Ajuste de arredondamento: joga diferença para a última linha
            diferenca = currency.round(discount_value_total - soma_descontos)
            if base_lines and diferenca:
                base_lines[-1].discount_value += diferenca

            # -------- Totais da fatura ----------
            total_final = currency.round(total - discount_value_total)

            inv.amount_price_gross = currency.round(total)
            inv.amount_discount_value = currency.round(discount_value_total)
            inv.amount_untaxed = currency.round(total)
            inv.amount_total = currency.round(total_final)
            inv.amount_residual = currency.round(total_final)
            inv.amount_total_signed = currency.round(total_final)
            inv.amount_untaxed_signed = currency.round(total_final)

    #def action_post(self):
    #    res = super(AccountMove, self).action_post()
    #    for inv in self:
    #        inv._compute_discounts()
    #    return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        result = super(AccountMoveLine, self.with_context(create_from_move_line=True)).create(vals_list)
        for values, line in zip(vals_list, result):
            discount = values.get("discount")
            discount_value = values.get("discount_value")
            quantity = values.get("quantity", 0)
            price_unit = values.get("price_unit", 0.0)
            if discount and discount_value and not line.discount_value:
                currency = line.currency_id or line.company_id.currency_id
                price_unit_discount = currency.round(price_unit * quantity * (discount / 100.0))
                line.discount_value = price_unit_discount

        return result   
    
    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        super(AccountMoveLine, self)._compute_totals()
        for line in self:
            if self.env.context.get('create_from_move_line'):
                continue
            currency = line.currency_id or line.company_id.currency_id
            price_unit_discount = currency.round(
                line.price_unit * line.quantity * (line.discount/100)
            )
            line.discount_value = price_unit_discount
