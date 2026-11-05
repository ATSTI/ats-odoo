# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import date

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    # tirei pq qdo recebe parcial nao mostra a data correta
    # payment_date = fields.Date(
    #     string="Data do Pagamento"
    # )

    number_nfe = fields.Char(
        # related="move_id.document_number",
        string="Nota Fiscal",
        compute="_compute_number_nfe",
        store=True,  # opcional, se quiser armazenar no banco
    )

    @api.depends("move_id", "move_id.name")
    def _compute_number_nfe(self):
        for rec in self:
            move = rec.move_id
            if not move:
                rec.number_nfe = False
                continue
            # Verificar se o campo document_number existe
            if hasattr(move, "document_number"):
                rec.number_nfe = move.document_number or move.name
            else:
                rec.number_nfe = move.name

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
