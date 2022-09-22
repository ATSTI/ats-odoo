# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'


    def _create_payment_vals_from_wizard(self):
        payment_vals = super()._create_payment_vals_from_wizard()
        for line in self.line_ids:
            line.write({'payment_date': fields.Date.context_today(self)})
        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            name = payment_vals['ref']
            payment_vals['write_off_line_vals'] = {
                'name': name,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
                'payment_date': fields.Date.context_today(self),
            }
        return payment_vals
