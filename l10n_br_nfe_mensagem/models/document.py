# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from nfelib.nfe.bindings.v4_0.nfe_v4_00 import Nfe


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"


    def _valida_xml(self, xml_file):
        self.ensure_one()
        import wdb
        wdb.set_trace()
        erros = Nfe.schema_validation(xml_file)
        erros = "\n".join(erros)
        lista_erros = erros.splitlines()
        for erros_msg in lista_erros:            
            max_len = erros_msg.find('maxLength')
            if max_len > 0:
                campo_erro = erros_msg[45:max_len-11]
                if campo_erro == "xLgr":
                    erros += " \n Rua + Bairro + Complemento: máximo 60 caracteres."
                if campo_erro == "xNome":
                    erros += " \n Nome: máximo 60 caracteres."
                if campo_erro == "xFant":
                    erros += " \n Razão social:máximo 60 caracteres."
            max_len = erros_msg.find('nro')
            max1_len = erros_msg.find('xBairro')
            if max_len > 0 and max_len > max1_len:
                erros += " \n Campo número no Endereço não preenchido."

        self.write({"xml_error_message": erros or False})