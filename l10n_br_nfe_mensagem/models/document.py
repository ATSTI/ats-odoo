# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from nfelib.nfe.bindings.v4_0.nfe_v4_00 import Nfe
from erpbrasil.base.fiscal.edoc import ChaveEdoc
import re


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"


    def _valida_xml(self, xml_file):
        self.ensure_one()
        erros = Nfe.schema_validation(xml_file)
        erros = "\n".join(erros)
        lista_erros = erros.splitlines()
        msg = set()
        for erros_msg in lista_erros:
            # TODO - colocar o LINK pra arrumar o erro
            # data-oe-model="stock.picking" t-att-data-oe-id="picking.id">
            # link_partner = "<a href=# data-oe-model=" + self.partner_id._name + " data-oe-id=" + str(self.partner_id.id) + ">CORRIGIR</a>"
            # link_partner = f"<a href=#id={self.partner_id.id}&model={self.partner_id._name}>CORRIGIR</a>"
            link_partner = ""
            erro_cep = erros_msg.find('CEP')
            if erro_cep > 0:
                msg.add(f" \n Erro no CEP informado.")
            max_len = erros_msg.find('maxLength')
            if max_len > 0:
                campo_erro = erros_msg[45:max_len-11]
                if campo_erro == "xLgr":
                    msg.add(f" \n Rua + Bairro + Complemento: máximo 60 caracteres. {link_partner}")
                if campo_erro == "xNome":
                    msg.add(f" \n Nome: máximo 60 caracteres.{link_partner}")
                if campo_erro == "xFant":
                    msg.add(f" \n Razão social: máximo 60 caracteres.{link_partner}")
                if campo_erro == "natOp":
                    msg.add(f" \n Natureza da Operação: máximo 60 caracteres.")

            max_len = erros_msg.find('CNPJ')
            max1_len = erros_msg.find('xNome')
            if max_len > 0 and max1_len > 0 and max_len > max1_len:
                msg.add(f" \n Campo Cnpj/Cpf não preenchido.{link_partner}")
            max_len = erros_msg.find('nro')
            max1_len = erros_msg.find('xBairro')
            if max1_len < 0:
                max1_len = erros_msg.find('xCpl')
            if max_len > 0 and max1_len > 0 and max_len > max1_len:
                msg.add(" \n Campo número no endereço do parceiro não preenchido." + link_partner)
        for doc in self.document_related_ids:
            if doc.document_key:
                doc_key = re.sub('[^0-9]', '', doc.document_key)
                if len(doc_key) < 44:
                    msg.add(f" \n Chave inválida: chave tem que ter 44 caracteres sem espaços.")
        if len(msg):
            mensagem = ""
            for m in list(msg):
                mensagem += m
            erros = m
        self.write({"xml_error_message": erros or False})
