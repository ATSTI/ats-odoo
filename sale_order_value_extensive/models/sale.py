from odoo import models, fields, api
from num2words import num2words


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    extensive_value = fields.Char(
        'Valor por Extenso', compute="_compute_extensive_value")

    #  Compute the extensive value of the invoice
    @api.depends('amount_total')
    def _compute_extensive_value(self):
        for record in self:
            val = record.amount_total
            val_ext = num2words(val, lang='pt_BR', to='currency')
            record.extensive_value = val_ext