
from odoo import models, _, api, fields
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFE,
 )


class AccountMove(models.Model):
    _inherit = "account.move"
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
      
    xml_error_message = fields.Text(
        readonly=True,
        string="XML validation errors",
        copy=False,
    )
  
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        result = super()._onchange_partner_id()
        self.xml_error_message = False
        if self.partner_id and self.document_type_id:
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
            if not self.partner_id.street_name:
                erros += "\n Cadastro do parceiro sem Rua."
            if not self.partner_id.street_number:
                erros += "\n Cadastro do parceiro sem NÚMERO."
            if not self.partner_id.district:
                erros += "\n Cadastro do parceiro sem Bairro."
            if not self.partner_id.city_id:
                erros += "\n Cadastro do parceiro sem CIDADE."
            if len(max) > 60:
                erros += "\n Rua + Bairro + Complemento deve ser menor que 60 caracteres."
            if self.partner_id.name and len(self.partner_id.name) > 60:
                erros += "\n Nome deve ser menor que 60 caracteres."
            if self.partner_id.legal_name and len(self.partner_id.legal_name) > 60:
                erros += "\n Razão social deve ser menor que 60 caracteres."
            if self.fiscal_operation_id.name and len(self.fiscal_operation_id.name) > 60:
                erros += "\n Natureza da operação deve ser menor que 60 caracteres."

            # erros = "\n".join(erros)
            self.xml_error_message = erros or False
        return result

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
