# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from datetime import date, datetime


class ImovelAlugarvender(models.TransientModel):

    _name = "imovel.alugarvender"
    _description = "Faturar Contratos"

    imovel_id = fields.Many2one('imovel', 'Imovel')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term", string="Condição de Pagamento", index=True
    )
    valor_aluguel = fields.Float(u'Valor Aluguel')
    comissao_percentual = fields.Float(u'Comissão imob.')
    comissao_valor = fields.Float(u'Valor Comissão')

    def action_aluga_executa(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

