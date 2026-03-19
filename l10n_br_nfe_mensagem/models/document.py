# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError  
from nfelib.nfe.bindings.v4_0.nfe_v4_00 import Nfe
import re

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFCE,
    MODELO_FISCAL_NFE,
    PROCESSADOR_OCA,
)

from erpbrasil.transmissao import TransmissaoSOAP
from erpbrasil.assinatura.excecoes import CertificadoExpirado
from nfelib.nfe.ws.edoc_legacy import NFCeAdapter as edoc_nfce
from nfelib.nfe.ws.edoc_legacy import NFeAdapter as edoc_nfe

from requests import Session


def filter_processador_edoc_nfe(record):
    if record.processador_edoc == PROCESSADOR_OCA and record.document_type_id.code in [
        MODELO_FISCAL_NFE,
        MODELO_FISCAL_NFCE,
    ]:
        return True
    return False

class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _edoc_processor(self):
        if not self.filtered(filter_processador_edoc_nfe):
            return super()._edoc_processor()

        self._check_nfe_environment()
        try:
            certificado = self.company_id._get_br_ecertificate()
        except CertificadoExpirado:
            raise UserError("Certificado digital expirado. Atualize o certificado.")
        session = Session()
        session.verify = False

        params = {
            "transmissao": TransmissaoSOAP(certificado, session),
            "uf": self.company_id.state_id.ibge_code,
            "versao": self.nfe_version,
            "ambiente": self.nfe_environment,
        }

        if self.document_type == MODELO_FISCAL_NFE:
            params.update(
                envio_sincrono=self.company_id.nfe_enable_sync_transmission,
                contingencia=self.company_id.nfe_enable_contingency_ws,
            )
            return edoc_nfe(**params)

        if self.document_type == MODELO_FISCAL_NFCE:
            params.update(
                csc_token=self.company_id.nfce_csc_token,
                csc_code=self.company_id.nfce_csc_code,
            )
            return edoc_nfce(**params)

    def action_document_send(self):
        result = super().action_document_send()
        # self._action_document_send()
        for event in self.event_ids:
            if event.status_code == "100":
                self.write({"xml_error_message": False})
                break
            if event.status_code:
                self.write({"xml_error_message": event.response})
        return result 

    def _validate_xml(self, xml_file):
        self.ensure_one()
        if not self.filtered(filter_processador_edoc_nfe):
            return super()._validate_xml(xml_file)
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
                    msg.add(f" \n Razão social: máximo 60 caracteres.{link_partner}")
                if campo_erro == "xFant":
                    msg.add(f" \n Nome: máximo 60 caracteres.{link_partner}")
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
        # usa certificado A3, entao remove o erro de assinatura
        if not (self.company_id.sudo().certificate_nfe_id or self.company_id.sudo().certificate_ecnpj_id):
            if 'Signature' in erros:
                erros = ''
        self.write({"xml_error_message": erros or False})

