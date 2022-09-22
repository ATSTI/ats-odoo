# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import date

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="move_id.partner_id",
        string="Partner",
        store=True
    )

    payment_date = fields.Date(
        string="Data do Pagamento"
    )

    number_nfe = fields.Char(
        related="move_id.document_number",
        string="Nota Fiscal",
    )

    def action_register_payment_move_line(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move.line',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }