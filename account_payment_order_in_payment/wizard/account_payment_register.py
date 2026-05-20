# -*- coding: utf-8 -*-

from odoo import models, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # necessario para baixar uma fatura usando outro metodo e nao gerar linha no cnab
    # sem isso, gera uma linha pra enviar ao banco para baixar o boleto
    def _create_payment_vals_from_wizard(self, batch_result):
        if self.payment_method_line_id.code == "manual":
            payment_mode = self.env['account.payment.mode'].search([('fixed_journal_id', '=', self.journal_id.id)], limit=1)
            if payment_mode:
                pay_line = self.line_ids[0].payment_line_ids
                pay_line.write({'state': 'cancel'})
                self.line_ids[0].move_id.write({'payment_mode_id': payment_mode.id})
        return super()._create_payment_vals_from_wizard(batch_result)
