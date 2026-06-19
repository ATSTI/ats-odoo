# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Document model for PRESCON NFSe integration."""

import base64
import logging
import dicttoxml
import xml.etree.ElementTree as ET

from datetime import datetime


from erpbrasil.base import misc

import pytz
import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    EVENT_ENV_HML,
    EVENT_ENV_PROD,
    SITUACAO_EDOC_AUTORIZADA,
    SITUACAO_EDOC_CANCELADA,
    SITUACAO_EDOC_REJEITADA,
    SITUACAO_FISCAL_CANCELADO
)
from odoo.addons.l10n_br_fiscal_edi.models.document import Document as FiscalDocument
from odoo.addons.l10n_br_nfse.models.document import filter_processador_edoc_nfse

from .constants import (
    NFSE_URL,
    TIMEOUT,
)
from .helpers import (
    _is_valid_pdf,
    filter_prescon,
    filter_prescon_nacional,
)

_logger = logging.getLogger(__name__)


class Document(models.Model):
    """Document model with Prescon NFSe integration."""

    _inherit = "l10n_br_fiscal.document"


    def make_prescon_nfse_pdf(self, content):
        """Generate a PDF for a NFSe document using PRESCON NFSe service.

        Parameters:
            - content: The binary content of the PDF to be attached.

        Returns:
            None. Creates or updates an 'ir.attachment' record with the PDF content.
        """
        if not self.filtered(filter_processador_edoc_nfse).filtered(filter_prescon):
            return super().make_pdf()
        else:
            if self.document_number:
                filename = "NFS-e-" + self.document_number + ".pdf"
            else:
                filename = "RPS-" + self.rps_number + ".pdf"

            vals_dict = {
                "name": filename,
                "res_model": self._name,
                "res_id": self.id,
                "datas": base64.b64encode(content),
                "mimetype": "application/pdf",
                "type": "binary",
            }
            if self.file_report_id:
                self.file_report_id.write(vals_dict)
            else:
                self.file_report_id = self.env["ir.attachment"].create(vals_dict)

    def _prepare_prestador(self):
        num_rps = self.rps_number or 0
        return {
            "data_emissao": fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(self.document_date)
            ).strftime("%d/%m/%Y"),
            "im": misc.punctuation_rm(self.company_id.prescon_code),
            "numeroRps": num_rps,
            "loteRps": "1"
        }

    def _prepare_dados_servico(self):
        return {
            "bairro": self.partner_id.district,
            "cep": misc.punctuation_rm(self.partner_id.zip) or "",
            "cidade": self.partner_id.city_id.name or "",
            "complemento": self.partner_id.street2 or "",
            "logradouro": self.partner_id.street or "",
            "numero": self.partner_id.street_number or "",
            "pais": self.partner_id.country_id.name or "",
            "uf": self.partner_id.state_id.code or "",
        }

    def _prepare_dados_tomador(self):
        return {
            "nomeTomador": self.partner_id.name or "",
            "tipoDoc": "J" if self.partner_id.company_type == "company" else "F",
            "documento": self.partner_id.cnpj_cpf_stripped or "",
            "ie": misc.punctuation_rm(self.partner_id.inscr_est) or "",
            "email": self.partner_id.email or "",
            "cep": misc.punctuation_rm(self.partner_id.zip) or "",
            "logradouro": self.partner_id.street or "",
            "numero": self.partner_id.street_number or "",
            "complemento": self.partner_id.street2 or "",
            "bairro": self.partner_id.district,
            "cidade": self.partner_id.city_id.name or "",
            "uf": self.partner_id.state_id.code or "",
            "pais": self.partner_id.country_id.name or "",
        }

    def _prepare_detalhe_servico(self):
        itens = {}
        for line in self.fiscal_line_ids:
            itens = {
                "aliquota": line.issqn_percent or 0,
                "codigo": misc.punctuation_rm(line.service_type_id.code),
                "nbs": misc.punctuation_rm(line.nbs_id.code),
                "descricao": line.name[:100] if line.name else "Servico",
                "valor": self.amount_financial_total,
            }
        return {
            "cofins": self.amount_cofins_value or 0,
            "csll": self.amount_csll_value or 0,
            "deducaoMaterial": 0,
            "descontoIncondicional": 0,
            "inss": self.amount_inss_value or 0,
            "ir": self.amount_irpj_value or 0,
            "issRetido": self.amount_issqn_wh_value,
            "item": itens,
            "obs": self.manual_customer_additional_data + " " + self.manual_fiscal_additional_data or "",
            "pisPasep": self.amount_pis_value or 0
        }

    def _serialize(self, edocs):
        edocs = super()._serialize(edocs)
        
        # Handle NFSe Nacional (original)
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_prescon
        ):
            edoc = {"notaFiscal": {
                "dadosPrestador": record._prepare_prestador(),
                "dadosServico": record._prepare_dados_servico(),
                "dadosTomador": record._prepare_dados_tomador(),
                "detalheServico": record._prepare_detalhe_servico(),
            }}
            edocs.append(edoc)
        return edocs

    def _document_export(self, pretty_print=True):
        for record in self.filtered(filter_processador_edoc_nfse):
            if record.company_id.provedor_nfse:
                edoc = record.serialize()[0]
                xml_file = dicttoxml.dicttoxml(edoc, custom_root="nfe", attr_type=False)
                event_id = self.event_ids.create_event_save_xml(
                    company_id=self.company_id,
                    environment=(
                        EVENT_ENV_PROD
                        if self.nfse_environment == "1"
                        else EVENT_ENV_HML
                    ),
                    event_type="0",
                    xml_file=xml_file.decode("utf-8"),
                    document_id=self,
                )
                _logger.debug(xml_file)
                record.authorization_event_id = event_id

    def _parse_authorization_datetime(self, data_emissao_str):
        aware_datetime = datetime.strptime(
            data_emissao_str, "%d/%m/%Y"
        )
        utc_datetime = aware_datetime.astimezone(pytz.utc)
        return utc_datetime.replace(tzinfo=None)

    def _fetch_pdf_from_urls(self, record, pdf_url, use_url_first=False):
        try:
            pdf_content = requests.get(pdf_url, verify=False).content
            return pdf_content
        except Exception as e:
            _logger.warning("Failed to fetch PDF from %s: %s", pdf_url, e)

    def _document_status(self):
        """Check and update the status of the NFSe document.

        Parameters:
            None.

        Returns:
            A string indicating the current status of the document.
        """
        result = super()._document_status()
        # Handle NFSe Municipal (original)
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_prescon_nacional
        ):
            result = self._process_status_nacional(record)

        return result

    # def create_cancel_event(self, status_json, record):
    #     """Create a cancel event and process it.

    #     Parameters:
    #         record: The NFSe record that is being canceled.

    #     Returns:
    #         The created event.
    #     """
    #     xml_path = status_json.get("caminho_xml_cancelamento", "")
    #     xml = ""
    #     if xml_path:
    #         xml = requests.get(
    #             NFSE_URL[record.nfse_environment] + xml_path,
    #             timeout=TIMEOUT,
    #             verify=record.company_id.nfse_ssl_verify,
    #         ).content.decode("utf-8")

    #     event = record.event_ids.create_event_save_xml(
    #         company_id=record.company_id,
    #         environment=(
    #             EVENT_ENV_PROD if record.nfse_environment == "1" else EVENT_ENV_HML
    #         ),
    #         event_type="2",
    #         xml_file="",
    #         document_id=record,
    #     )
    #     event.set_done(
    #         status_code=4,
    #         response=_("Successfully Processed"),
    #         protocol_date=fields.Datetime.to_string(fields.Datetime.now()),
    #         protocol_number="",
    #         file_response_xml=xml,
    #     )
    #     return event

    # def fetch_and_verify_pdf_content(self, status_json, record):
    #     """Fetch and verify the PDF content from the provided URL.

    #     Parameters:
    #         status_json: JSON response containing the URLs for the PDF.
    #         record: The NFSe record for which the PDF is being retrieved.

    #     Returns:
    #         None. Updates the record with the PDF content if valid.
    #     """
    #     pdf_content = requests.get(
    #         status_json["url"],
    #         timeout=TIMEOUT,
    #         verify=record.company_id.nfse_ssl_verify,
    #     ).content
    #     if not _is_valid_pdf(pdf_content):
    #         pdf_content = requests.get(
    #             status_json["url_danfse"],
    #             timeout=TIMEOUT,
    #             verify=record.company_id.nfse_ssl_verify,
    #         ).content
    #     if _is_valid_pdf(pdf_content):
    #         record.make_focus_nfse_pdf(pdf_content)

    def _process_cancel_base(
        self,
        record,
        ref,
        query_method,
        cancel_method,
        use_url_first=False,
    ):
        # Perform cancellation
        response = cancel_method(
            ref, record.cancel_reason, record.company_id, record.nfse_environment
        )
        retorno = response.text
        retorno = retorno.replace("\n", "")
        root = ET.fromstring(retorno)
        msg = ""
        code = ""
        for child in root[0]:
            if child.tag == "statusEmissao":
                code = child.text
            if child.tag == "messages":
                msg = child.text
        if response.status_code == 200 and code == '200':
            self.cancel_event_id = self.event_ids.create_event_save_xml(
               company_id=self.company_id,
                environment=(
                    EVENT_ENV_PROD if self.nfse_environment == "1" else EVENT_ENV_HML
                ),
                event_type="2",
                xml_file=retorno,
                document_id=self,
            )
            # record.write({
            #     'state_fiscal': SITUACAO_FISCAL_CANCELADO,
            #     'state_edoc': SITUACAO_EDOC_CANCELADA
            # })
            # record._document_cancel(record.cancel_reason)
            return response
        else:
            raise UserError(
                _(
                    "%(code)s - %(msg)s",
                    code=code,
                    msg=msg,
                )
            )

    def _process_cancel_municipal(self, record):
        """Process cancellation for NFSe Municipal."""
        ref = record.document_number
        nfse = record.env["prescon.nfse.nacional"]
        def cancel_method(ref, cancel_reason, company, environment):
            return nfse.cancel_prescon_nfse_document(
                ref, cancel_reason, company, environment
            )
        result = self._process_cancel_base(
            record,
            ref,
            None,
            cancel_method,
            use_url_first=True,
        )
        return result 

    def cancel_document_prescon(self):
        # Handle NFSe Municipal (original)
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_prescon
        ):
            return self._process_cancel_municipal(record)

    def _process_send_nacional(self, record):
        """Process document send for NFSe Nacional."""
        for edoc in record.serialize():
            ref = str(record.rps_number)
            xml_file = dicttoxml.dicttoxml(edoc, custom_root="nfe", attr_type=False)
            response = self.env[
                "prescon.nfse.nacional"
            ].process_prescon_nfse_nacional_document(
                xml_file, ref, record.company_id, record.nfse_environment
            )
            # modelo resposta
            # <nfeResposta>
            # <notaFiscal>
            # <numeroNota></numeroNota>
            # <numeroRps>198</numeroRps>
            # <loteRps></loteRps>
            # <codigoVerificacao></codigoVerificacao>
            # <link></link>
            # <cnpjPrestador></cnpjPrestador>
            # <dataEmissaoRPS>22/04/2026</dataEmissaoRPS>
            # <dataEmissaoNF></dataEmissaoNF>
            # <statusEmissao>400</statusEmissao>
            # <messages>O numero de RPS 198 ja existe.</messages>
            # </notaFiscal>
            # </nfeResposta>
            retorno = response.text
            xml_file = retorno.replace("\n", "")
            root = ET.fromstring(retorno)
            # xml_file = dicttoxml.dicttoxml(retorno, custom_root="nfe", attr_type=False)
            messages = ""
            status_emissao = ""
            numero_nota = ""
            codigo_verificacao = ""
            link = ""
            for child in root[0]:
                if child.tag == "statusEmissao":
                    status_emissao = child.text
                elif child.tag == "messages":
                    messages = child.text
                elif child.tag == "numeroNota":
                    numero_nota = child.text
                elif child.tag == "codigoVerificacao":
                    codigo_verificacao = child.text
                elif child.tag == "dataEmissaoRPS":
                    dataEmissaoRPS = child.text
                elif child.tag == "link":
                    link = child.text                    

            protocol_date = self._parse_authorization_datetime(dataEmissaoRPS)

            if response.status_code != 200 or str(status_emissao) != '200':
                # if retorno.get("statusEmissao") != 200:
                record._change_state(SITUACAO_EDOC_REJEITADA)
                raise UserError(
                    _(
                        "%(status)s - %(msg)s",
                        status=status_emissao,
                        msg=messages,
                    )
                )                        
            elif response.status_code == 200 and str(status_emissao) == '200':
                record.authorization_event_id.set_done(
                    status_code=4,
                    response=_("Processado com Sucesso"),
                    protocol_date=protocol_date,
                    protocol_number=codigo_verificacao,
                    file_response_xml=xml_file,
                )
                record.write(
                    {
                        "verify_code": codigo_verificacao,
                        "document_number": numero_nota,
                        "authorization_date": protocol_date,
                    }
                )
                # Se precisar do link da nota tem no EVENTO
                record._change_state(SITUACAO_EDOC_AUTORIZADA)
                if link:
                    retorno_pdf = self._fetch_pdf_from_urls(record, link, use_url_first=True)
                    self.make_prescon_nfse_pdf(retorno_pdf)

    def _eletronic_document_send(self):
        """Send the electronic document to the NFSe provider.

        Parameters:
            None.

        Returns:
            None. Updates the document's status based on the response.
        """
        res = super()._eletronic_document_send()
        # Handle NFSe Nacional (original)
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_prescon
        ):
            self._process_send_nacional(record)
        return res

    def _exec_before_SITUACAO_EDOC_CANCELADA(self, old_state, new_state):
        """Hook method before changing document's state to 'Cancelled'.

        Parameters:
            - old_state: The document's previous state.
            - new_state: The new state.

        Returns:
            The result of the cancellation process.
        """
        super()._exec_before_SITUACAO_EDOC_CANCELADA(old_state, new_state)
        return self.cancel_document_prescon()

    def _exec_after_SITUACAO_EDOC_CANCELADA(self, old_state, new_state):
        super()._exec_before_SITUACAO_EDOC_CANCELADA(old_state, new_state)
        self.state_edoc = SITUACAO_EDOC_CANCELADA

    @api.model
    def _cron_document_status_prescon(self):
        """Scheduled method to check the status of sent NFSe documents.

        Parameters:
            None.

        Returns:
            None. Updates the status of each document based on the NFSe provider's
            response.
        """
        records = (
            self.search([("state_edoc", "in", ["a_enviar"])], limit=25)
            .filtered(filter_processador_edoc_nfse)
            .filtered(filter_prescon)
        )
        # Iterate over each record individually, as _document_status()
        # may expect a singleton in some cases
        for record in records:
            record._document_status()
