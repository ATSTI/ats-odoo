# -*- coding: utf-8 -*-

from odoo import models, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def _get_batch_communication(self, batch_result):
        ''' Carrega na linha do pagamento o número da fatura
        '''
        labels = set(line.move_id.name or line.name or line.move_id.ref or line.move_id.name for line in batch_result['lines'])
        return ' '.join(sorted(labels))