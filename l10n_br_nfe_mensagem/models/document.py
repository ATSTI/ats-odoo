# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from nfelib.nfe.bindings.v4_0.nfe_v4_00 import Nfe


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"


    def _valida_xml(self, xml_file):
        self.ensure_one()
        erros = Nfe.schema_validation(xml_file)
        erros = "\n".join(erros)
        lista_erros = erros.splitlines()
        msg = ""
        for erros_msg in lista_erros:
            # import pudb;pu.db
            # data-oe-model="stock.picking" t-att-data-oe-id="picking.id">
            # link_partner = f"<a href=# data-oe-model='{self.partner_id._name}' data-oe-id='{self.partner_id.id}'>CORRIGIR</a>"
            # link_partner = f"<a href=#id={self.partner_id.id}&model={self.partner_id._name}>CORRIGIR</a>"
            link_partner = ""
            max_len = erros_msg.find('maxLength')
            if max_len > 0:
                campo_erro = erros_msg[45:max_len-11]
                if campo_erro == "xLgr":
                    msg += f" \n Rua + Bairro + Complemento: máximo 60 caracteres. {link_partner}"
                if campo_erro == "xNome":
                    msg += f" \n Nome: máximo 60 caracteres.{link_partner}"
                if campo_erro == "xFant":
                    msg += f" \n Razão social: máximo 60 caracteres.{link_partner}"
            max_len = erros_msg.find('CNPJ')
            max1_len = erros_msg.find('xNome')
            if max_len > 0 and max1_len > 0 and max_len > max1_len:
                msg += f" \n Campo Cnpj/Cpf não preenchido.{link_partner}"
            max_len = erros_msg.find('nro')
            max1_len = erros_msg.find('xBairro')
            if max1_len < 0:
                max1_len = erros_msg.find('xCpl')
            if max_len > 0 and max1_len > 0 and max_len > max1_len:
                msg += " \n Campo número no Endereço não preenchido." + link_partner
        if msg:
            erros = msg
        self.write({"xml_error_message": erros or False})