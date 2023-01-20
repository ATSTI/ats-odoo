# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ImovelAlugarvender(models.TransientModel):

    _name = "imovel.alugarvender"
    _description = "Faturar Contratos"

    imovel_id = fields.Many2one('imovel', 'Imovel')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term", string="Condição de Pagamento", index=True
    )
    valor_aluguel = fields.Float(u'Valor Aluguel')
    valor_venda = fields.Float(u'Valor Venda')
    comissao_percentual = fields.Float(u'Comissão imob.')
    comissao_valor = fields.Float(u'Valor Comissão')

    def action_aluga_executa(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        ctx = {
            'default_imovel_id': 'sale.order',
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

    def gera_fatura(self):

        # TODO - Colocar Diario na tela
        #      - Data da venda

        vals = {}
        msg = ''
        move = self.env['account.move']
        product = self.env['product.product']
        partner = self.env['res.partner']
        user = self.env['res.users']
        payment = self.env['account.payment.mode']
        _logger.info('numero de linhas da planilha %s', 5)

        vals['journal_id'] = self.journal_id.id
        vals['currency_id'] = 6
        vals['narration'] = f"Venda imovél"
        vals['invoice_date'] = 1
        vals['date'] = 2

        # verifica se ja existe uma fatura criada nesta data
        # search_invoice = move.search(
        #                 [('ref', '=', vals['ref']), ('partner_id', '=', vals['partner_id'])], limit=1)

        invoice = move.create(vals)
        if invoice:
            product_id = product.search([
                ("name", "ilike", "comissão")
            ], limit=1)
            invoice.invoice_line_ids = [(0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': self.comissao_valor,
                'name': f"{product.name} - {self.imovel_id.name}"
                # 'fiscal_operation_id': 14,
                # 'fiscal_operation_line_id': 26,
                # 'cfop_id': cfop_id.id if cfop_id else cfop_1949.id,
            })]
            invoice._onchange_invoice_line_ids()
            _logger.info('Invoice created: %s', invoice.id)

            msg += f"<br> Fatura criada: : {invoice.name}"
            self.message_post(
                body=msg,
                subject=_('Fatura criada pelo imovel.'),
                message_type='notification'

    @api.onchange('comissao_percentual')
    def onchange_comissao_percentual(self):
        if self.comissao_percentual:
            self.comissao_valor = self.valor_aluguel * (float(self.comissao_percentual)/100)

    @api.onchange('comissao_percentual')
    def onchange_comissao_percentual(self):
        if self.comissao_percentual:
            self.comissao_valor = self.valor_venda * (float(self.comissao_percentual)/100)

