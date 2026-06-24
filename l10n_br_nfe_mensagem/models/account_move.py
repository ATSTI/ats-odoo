# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import re
from odoo import models, _, api, fields
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFE,
 )
from odoo.addons.l10n_br_account_payment_order.constants import (
    BR_CODES_PAYMENT_ORDER,
 )

class AccountMove(models.Model):
    _inherit = "account.move"

    # xml_error_message = fields.Text(
    #     readonly=True,
    #     string="XML validation errors",
    #     copy=False,
    # )
  
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self._valida_cadastro()
        return super()._onchange_partner_id()

    @api.onchange("document_type_id")
    def _onchange_document_type_id(self):
        self._valida_cadastro()

    @api.onchange("payment_mode_id")
    def _onchange_payment_mode_id(self):
        self._valida_cadastro()

    def _valida_cadastro(self):
        self.xml_error_message = False
        nfe = self.partner_id \
            and self.document_type_id.code == MODELO_FISCAL_NFE
        if (
            nfe
            or (
                self.payment_mode_id.payment_method_code in BR_CODES_PAYMENT_ORDER
            )
        ):
            max = ""
            if self.partner_id.street_name and self.partner_id.district:
                max = self.partner_id.street_name or "" + self.partner_id.street2 or "" + self.partner_id.district or ""
            # tratar erros
            erros = ""
            if not self.partner_id.legal_name:
                erros += "\n Cadastro do parceiro sem Razão social."
            if not self.partner_id.cnpj_cpf:
                erros += "\n Cadastro do parceiro sem CNPJ/CPF."
            if not self.partner_id.zip:
                erros += "\n Cadastro do parceiro sem CEP."
            if self.partner_id.zip:
                cep = re.sub('[^0-9]', '', self.partner_id.zip)
                if not len(cep) == 8:
                    erros += "\n CEP errado no cadastro."
            if not self.partner_id.street_name:
                erros += "\n Cadastro do parceiro sem Rua."
            if not self.partner_id.street_number:
                erros += "\n Cadastro do parceiro sem NÚMERO."
            if not self.partner_id.district:
                erros += "\n Cadastro do parceiro sem Bairro."
            if not self.partner_id.city_id:
                erros += "\n Cadastro do parceiro sem CIDADE."
            if self.partner_id.phone:
                fone = re.sub('[^0-9]', '', self.partner_id.phone)
                if len(fone) > 13:
                    erros += "\n Número de telefone inválido."
            if nfe and len(max) > 60:
                erros += "\n Rua + Bairro + Complemento deve ser menor que 60 caracteres."
            if (
                nfe
                and self.partner_id.name
                and len(self.partner_id.name) > 60
            ):
                erros += "\n Nome deve ser menor que 60 caracteres."
            if (
                nfe
                and self.partner_id.legal_name
                and len(self.partner_id.legal_name) > 60
            ):
                erros += "\n Razão social deve ser menor que 60 caracteres."
            
            if (
                nfe
                and self.fiscal_operation_id.name
                and len(self.fiscal_operation_id.name) > 60
            ):
                erros += "\n Natureza da operação deve ser menor que 60 caracteres."

            # erros = "\n".join(erros)
            self.xml_error_message = erros or False

    def action_post(self):
        if self.document_type_id and self.document_type_id.code in (
                MODELO_FISCAL_NFE
        ):
            item = 0
            msg = ""
            for line in self.invoice_line_ids:                
                if not line.icms_cst_id:
                    item += 1
                    msg += f"\n {item} - {line.name};"
            if msg:
                msg = f"{'Item' if item == 1 else 'Itens'} sem informação do CST do ICMS: \n {msg}"
                raise UserError(_(msg))
        return super().action_post()
