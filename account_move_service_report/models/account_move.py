from odoo import models, fields, api, tools
from num2words import num2words
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    extensive_value = fields.Char(
        'Valor por Extenso', compute="_compute_extensive_value", store=True)


    #  Compute the extensive value of the invoice
    @api.depends('amount_total')
    def _compute_extensive_value(self):
        for record in self:
            val = record.amount_total
            val_ext = num2words(val, lang='pt_BR', to='currency')
            record.extensive_value = val_ext