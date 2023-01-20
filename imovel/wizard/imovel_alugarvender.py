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
        move = self.env['account.move']
        product = self.env['product.product']
        partner = self.env['res.partner']
        user = self.env['res.users']
        payment = self.env['account.payment.mode']
        fiscal = self.env['account.fiscal.position']
        operation = self.env['l10n_br_fiscal.operation']
        operation_line = self.env['l10n_br_fiscal.operation.line']
        cfop = self.env['l10n_br_fiscal.cfop']
        document_type = self.env['l10n_br_fiscal.document.type']
        document_serie = self.env['l10n_br_fiscal.document.serie']
        _logger.info('numero de linhas da planilha %s', 5)
        vals['journal_id'] = self.journal_id.id
        vals['document_type_id'] = 1
        vals['fiscal_operation_id'] = 14
        vals['currency_id'] = 6
        vals['document_number'] = 8
        vals['journal_id'] = self.journal_id.id
        vals['narration'] = 'Linha %s' % 5
        vals['invoice_date'] = 1
        vals['date'] = 2
        vals['invoice_date_due'] = 3

    @api.onchange('comissao_percentual')
    def onchange_comissao_percentual(self):
        if self.comissao_percentual:
            self.comissao_valor = self.valor_aluguel * (float(self.comissao_percentual)/100)

    @api.onchange('comissao_percentual')
    def onchange_comissao_percentual(self):
        if self.comissao_percentual:
            self.comissao_valor = self.valor_venda * (float(self.comissao_percentual)/100)

