# -*- coding: utf-8 -*-

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
            inv._compute_amount()
        return True
    
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        for inv in self:
            if inv.discount_type and inv.discount_rate:
                currency = inv.currency_id or self.env.company.currency_id
                total = sum(line.quantity * line.price_unit for line in inv.invoice_line_ids)
                discount_value_total = 0.0

                if total == 0:
                    inv.amount_untaxed = inv.amount_discount_value = inv.amount_total = 0.0
                    continue

                # Determina tipo de desconto
                if inv.discount_type == 'percent':
                    discount_percent = inv.discount_rate
                else:
                    discount_percent = (inv.discount_rate / total) * 100 if inv.discount_rate else 0.0

                for line in inv.invoice_line_ids:
                    if not line.quantity or not line.price_unit:
                        continue
                    price_unit_discount = currency.round(
                        line.price_unit * line.quantity * (discount_percent / 100.0)
                    )
                    line.discount_value = price_unit_discount
                    discount_value_total += price_unit_discount

                    try:
                        line._compute_totals()
                    except AttributeError:
                        pass
                inv.amount_untaxed = currency.round(total)
                if inv.discount_type == 'amount':   
                    if inv.discount_rate != currency.round(discount_value_total):
                        discount_value_total = discount_value_total + inv.discount_rate - currency.round(discount_value_total)
                else:
                    discount_value_total = (discount_percent / 100.0) * total   
                total_final = currency.round(total - discount_value_total)
                inv.amount_discount_value = currency.round(discount_value_total)
                inv.amount_total = total_final 
                inv.amount_residual = inv.amount_total - inv.amount_paid
                inv.amount_total_signed = total_final
                inv.amount_untaxed_signed = total_final
                inv.amount_total_in_currency_signed = total_final
            if inv.discount_type is False or inv.discount_rate == 0.0:
                for line in inv.invoice_line_ids:
                    line.discount_value = 0.0
                inv.amount_discount_value = 0.0

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
                line.price_unit * line.quantity * (line.discount / 100.0)
            )
            line.discount_value = price_unit_discount