# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from collections import defaultdict


class AccountMove(models.Model):

    _inherit = "account.move"

    cpf_consumidor = fields.Char('CNPJ/CPF Consumidor')

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        result = super()._onchange_partner_id()
        if self.partner_id and self.partner_id.is_anonymous_consumer and self.partner_id.cnpj_cpf:
            self.partner_id.write({'cnpj_cpf': False})
        return result
    
    @api.onchange("cpf_consumidor")
    def _onchange_cpf_consumidor(self):
        if self.cpf_consumidor:
            self.partner_id.write({'cnpj_cpf': self.cpf_consumidor})

    @api.onchange("document_type_id")
    def _onchange_document_type_id(self):
        result = super()._onchange_document_type_id()
        if self.document_type_id and self.document_type_id.code == '65':
            self.ind_pres = '1'
        return result
