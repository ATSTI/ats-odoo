from odoo import models


class SaleOrder(models.Model):
    _inherit='sale.order'



    def action_confirm(self):
        result = super().action_confirm()
        self.message_error_partner = False
        if self.partner_id and self.fiscal_operation_id:
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
            if len(max) > 60:
                erros += "\n Rua + Bairro + Complemento deve ser menor que 60 caracteres."
            if self.partner_id.name and len(self.partner_id.name) > 60:
                erros += "\n Nome deve ser menor que 60 caracteres."
            if self.partner_id.legal_name and len(self.partner_id.legal_name) > 60:
                erros += "\n Razão social deve ser menor que 60 caracteres."
            # if self.fiscal_operation_id.name and len(self.fiscal_operation_id.name) > 60:
            #     erros += "\n Natureza da operação deve ser menor que 60 caracteres."

            # erros = "\n".join(erros)
            self.message_error_partner = erros or False
            if self.message_error_partner:
                raise models.ValidationError(
                    _("Erro no cadastro do parceiro: %s") % self.message_error_partner
                )
        for order in self:
            order.picking_ids.filtered(
                lambda p: p.state not in ('done', 'cancel')
            ).write({'state': 'draft'})
            
        return result