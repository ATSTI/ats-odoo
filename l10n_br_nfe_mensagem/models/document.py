# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"


    def _valida_xml(self, xml_file):
        self.ensure_one()
        erros = Nfe.schema_validation(xml_file)
        erros = "\n".join(erros)
        if erros:
            # import pudb;pu.db
            max_len = erros.find('maxLength')
            if max_len > 0:
                campo_erro = erros[45:max_len-9]
                if campo_erro == "xLgr":
                    erros += " \n Rua + Bairro + Complemento, tem que ser no máximo 60 caracteres"
        self.write({"xml_error_message": erros or False})