# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Document model for PRESCON NFSe integration."""

import base64
import logging
import dicttoxml
from datetime import datetime

from erpbrasil.edoc.edoc import DocumentoEletronico
from nfelib.nfse.bindings.v1_0.nfse_v1_00 import Nfse
from erpbrasil.base import misc
from erpbrasil.edoc.provedores.cidades import NFSeFactory
from erpbrasil.transmissao import TransmissaoSOAP
from requests import Session

import pytz
import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    EVENT_ENV_HML,
    EVENT_ENV_PROD,
    SITUACAO_EDOC_AUTORIZADA,
    SITUACAO_EDOC_CANCELADA,
    SITUACAO_EDOC_ENVIADA,
    SITUACAO_EDOC_REJEITADA,
)
from odoo.addons.l10n_br_fiscal_edi.models.document import Document as FiscalDocument
from odoo.addons.l10n_br_nfse.models.document import filter_processador_edoc_nfse

from .constants import (
    CODE_NFE_AUTORIZADA,
    CODE_NFE_CANCELADA,
    NFSE_URL,
    STATUS_AUTORIZADO,
    STATUS_CANCELADO,
    STATUS_ERRO_AUTORIZACAO,
    STATUS_PROCESSANDO_AUTORIZACAO,
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
        # <bairro>CENTRO</bairro>
        # <cep>13163338</cep>
        # <cidade>Artur Nogueira</cidade>
        # <complemento>TERREO</complemento>
        # <logradouro>Rua Continental</logradouro>
        # <numero>345</numero>
        # <pais>BRASIL</pais>
        # <uf>SP</uf>
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
        # <nomeTomador>GUSTAVO GONCALVES</nomeTomador>
        # <tipoDoc>J</tipoDoc>
        # <documento>63101149000187</documento>
        # <ie/>
        # <email/>
        # <cep>13215791</cep>
        # <logradouro>Rua Ostenda</logradouro>
        # <numero>93</numero>
        # <complemento>Sala 23A</complemento>
        # <bairro>Vila Vermelha</bairro>
        # <cidade>Jundiai</cidade>
        # <uf>SP</uf>
        # <pais>BRASIL</pais>
        return {
            "nomeTomador": self.partner_id.name or "",
            "tipoDoc": "J" if self.partner_id.company_type == "company" else "F",
            "documento": self.partner_id.cnpj_cpf_stripped or "",
            "ie": misc.punctuation_rm(self.partner_id.l10n_br_ie_code) or "",
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
        # <detalheServico>
        # <cofins>0</cofins>
        # <csll>0</csll>
        # <deducaoMaterial>0</deducaoMaterial>
        # <descontoIncondicional>0</descontoIncondicional>
        # <inss>0</inss>
        # <ir>0</ir>
        # <issRetido>0</issRetido>
        # <item>
        # <aliquota>2.01</aliquota>
        # <codigo>107</codigo>
        # <nbs>115013000</nbs>
        # <descricao>PRESTACAO DE SERVICOS</descricao>
        # <valor>36.00</valor>
        # </item>
        # <obs>Servicos realizados online</obs>
        # <pisPasep>0</pisPasep>
        # </detalheServico>
        itens = {}
        for line in self.fiscal_line_ids:
            itens = {
                "aliquota": line.issqn_percent or 0,
                "codigo": misc.punctuation_rm(line.service_type_id.code),
                "nbs": misc.punctuation_rm(line.nbs_id.code),
                "descricao": line.name[:100] if line.name else "Servico",
                "valor": self.fiscal_amount_total,
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
            "obs": self.manual_fiscal_additional_data or "",
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
        # import pudb;pu.db
        # result = super()._document_export()
        for record in self.filtered(filter_processador_edoc_nfse):
            if record.company_id.provedor_nfse:
                edoc = record.serialize()[0]
                # processador = record._processador_erpbrasil_nfse()
                # nfse = Nfse.from_dict(edoc)
                xml_file = dicttoxml.dicttoxml(edoc, custom_root="nfe", attr_type=False)
                # xml_file = nfse.to_xml(pretty_print=pretty_print)
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
                # record.make_pdf()

    def _fetch_xml_from_path(self, record, xml_path):
        """Fetch XML content from the given path.

        Args:
            record: The document record.
            xml_path (str): Path to XML file.

        Returns:
            str: XML content as string, empty if path is invalid.
        """
        if not xml_path:
            return ""
        try:
            return requests.get(
                NFSE_URL[record.nfse_environment] + xml_path,
                timeout=TIMEOUT,
                verify=record.company_id.nfse_ssl_verify,
            ).content.decode("utf-8")
        except Exception as e:
            _logger.warning("Failed to fetch XML from %s: %s", xml_path, e)
            return ""

    def _fetch_pdf_from_urls(self, record, json_data, use_url_first=False):
        """Fetch PDF content from URLs in JSON data.

        Args:
            record: The document record.
            json_data (dict): JSON response data.
            use_url_first (bool): If True, try 'url' first, then 'url_danfse'.
                                 If False, only try 'url_danfse'.

        Returns:
            bytes: PDF content, or None if not found or invalid.
        """
        if record.company_id.focusnfe_nfse_force_odoo_danfse:
            return None

        pdf_url = None
        if use_url_first:
            pdf_url = json_data.get("url")
            if pdf_url:
                try:
                    pdf_content = requests.get(
                        pdf_url,
                        timeout=TIMEOUT,
                        verify=record.company_id.nfse_ssl_verify,
                    ).content
                    if _is_valid_pdf(pdf_content):
                        return pdf_content
                except Exception as e:
                    _logger.warning("Failed to fetch PDF from %s: %s", pdf_url, e)

        pdf_url = json_data.get("url_danfse", "")
        if pdf_url:
            try:
                pdf_content = requests.get(
                    pdf_url,
                    timeout=TIMEOUT,
                    verify=record.company_id.nfse_ssl_verify,
                ).content
                if _is_valid_pdf(pdf_content):
                    return pdf_content
            except Exception as e:
                _logger.warning("Failed to fetch PDF from %s: %s", pdf_url, e)

        return None

    def _process_authorized_status_base(
        self,
        record,
        json_data,
        verify_code_key="codigo_verificacao",
        use_url_first=False,
        xml_required=True,
    ):
        """Base method to process authorized status.

        Args:
            record: The document record.
            json_data (dict): JSON response data.
            verify_code_key (str): Key to get verification code from json_data.
            use_url_first (bool): Whether to try 'url' first for PDF.
            xml_required (bool): Whether XML path is required (municipal)
                or optional (nacional).
        """
        # naive_datetime = self._parse_authorization_datetime(json_data)
        verify_code = (
            json_data.get(verify_code_key, "")
            if verify_code_key
            else json_data.get("codigo_verificacao", "")
        )
        document_number = json_data.get("numero", "")

        record.write(
            {
                "verify_code": verify_code,
                "document_number": document_number,
                "authorization_date": naive_datetime,
            }
        )

        xml_path = json_data.get("caminho_xml_nota_fiscal", "")
        if xml_required and not xml_path:
            # Will raise KeyError if not present
            xml_path = json_data.get("caminho_xml_nota_fiscal")

        xml = self._fetch_xml_from_path(record, xml_path) if xml_path else ""

        if not record.authorization_event_id:
            record._document_export()

        if record.authorization_event_id:
            # For municipal, xml is required; for nacional, only if available
            if xml_required or xml:
                record.authorization_event_id.set_done(
                    status_code=4,
                    response=_("Successfully Processed"),
                    protocol_date=record.authorization_date,
                    protocol_number=record.authorization_protocol,
                    file_response_xml=xml,
                )
                record._change_state(SITUACAO_EDOC_AUTORIZADA)

                if record.company_id.focusnfe_nfse_force_odoo_danfse:
                    record.make_pdf()
                else:
                    pdf_content = self._fetch_pdf_from_urls(
                        record, json_data, use_url_first
                    )
                    if pdf_content:
                        record.make_focus_nfse_pdf(pdf_content)


    def _process_authorized_status_nacional(self, record, json_data):
        """Process authorized status for NFSe Nacional."""
        self._process_authorized_status_base(
            record,
            json_data,
            verify_code_key="codigo_verificacao",
            use_url_first=False,
            xml_required=False,
        )

    def _process_error_status(self, record, json_data):
        """Process error authorization status."""
        erros = json_data.get("erros", [])
        error_msg = erros[0]["mensagem"] if erros else _("Authorization error")
        record.write(
            {
                "edoc_error_message": error_msg,
            }
        )
        record._change_state(SITUACAO_EDOC_REJEITADA)

    def _process_status_nacional(self, record):
        """Process status check for NFSe Nacional."""
        ref = str(record.rps_number)
        response = record.env[
            "focusnfe.nfse.nacional"
        ].query_focus_nfse_nacional_by_ref(
            ref, record.company_id, record.nfse_environment
        )

        json = response.json()

        edoc_states = ["a_enviar", "enviada", "rejeitada"]
        if record.company_id.focusnfe_nfse_update_authorized_document_status:
            edoc_states.append("autorizada")

        if response.status_code == 200:
            if record.state in edoc_states:
                if (
                    json["status"] == STATUS_AUTORIZADO
                    and record.state_edoc != SITUACAO_EDOC_AUTORIZADA
                ):
                    self._process_authorized_status_nacional(record, json)
                elif json["status"] == STATUS_ERRO_AUTORIZACAO:
                    self._process_error_status(record, json)
                elif json["status"] == STATUS_CANCELADO:
                    if record.state_edoc != SITUACAO_EDOC_CANCELADA:
                        record._document_cancel(record.cancel_reason)

            return _(json["status"])

        return "Unable to retrieve the document status."

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

    def create_cancel_event(self, status_json, record):
        """Create a cancel event and process it.

        Parameters:
            record: The NFSe record that is being canceled.

        Returns:
            The created event.
        """
        xml_path = status_json.get("caminho_xml_cancelamento", "")
        xml = ""
        if xml_path:
            xml = requests.get(
                NFSE_URL[record.nfse_environment] + xml_path,
                timeout=TIMEOUT,
                verify=record.company_id.nfse_ssl_verify,
            ).content.decode("utf-8")

        event = record.event_ids.create_event_save_xml(
            company_id=record.company_id,
            environment=(
                EVENT_ENV_PROD if record.nfse_environment == "1" else EVENT_ENV_HML
            ),
            event_type="2",
            xml_file="",
            document_id=record,
        )
        event.set_done(
            status_code=4,
            response=_("Successfully Processed"),
            protocol_date=fields.Datetime.to_string(fields.Datetime.now()),
            protocol_number="",
            file_response_xml=xml,
        )
        return event

    def fetch_and_verify_pdf_content(self, status_json, record):
        """Fetch and verify the PDF content from the provided URL.

        Parameters:
            status_json: JSON response containing the URLs for the PDF.
            record: The NFSe record for which the PDF is being retrieved.

        Returns:
            None. Updates the record with the PDF content if valid.
        """
        pdf_content = requests.get(
            status_json["url"],
            timeout=TIMEOUT,
            verify=record.company_id.nfse_ssl_verify,
        ).content
        if not _is_valid_pdf(pdf_content):
            pdf_content = requests.get(
                status_json["url_danfse"],
                timeout=TIMEOUT,
                verify=record.company_id.nfse_ssl_verify,
            ).content
        if _is_valid_pdf(pdf_content):
            record.make_focus_nfse_pdf(pdf_content)

    def _handle_cancelled_status(self, record, status_json, use_url_first=False):
        """Handle already cancelled status.

        Args:
            record: The document record.
            status_json (dict): Status JSON response.
            use_url_first (bool): Whether to try 'url' first for PDF.
        """
        record.cancel_event_id = record.create_cancel_event(status_json, record)
        if record.company_id.focusnfe_nfse_force_odoo_danfse:
            record.make_pdf()
        else:
            if use_url_first:
                record.fetch_and_verify_pdf_content(status_json, record)
            else:
                url_danfse = status_json.get("url_danfse", "")
                if url_danfse:
                    pdf_content = requests.get(
                        url_danfse,
                        timeout=TIMEOUT,
                        verify=record.company_id.nfse_ssl_verify,
                    ).content
                    if _is_valid_pdf(pdf_content):
                        record.make_focus_nfse_pdf(pdf_content)

    def _process_cancel_base(
        self,
        record,
        ref,
        query_method,
        cancel_method,
        use_url_first=False,
        apply_barueri_hack=False,
    ):
        """Base method to process cancellation.

        Args:
            record: The document record.
            ref (str): Document reference.
            query_method: Method to query document status.
            cancel_method: Method to cancel document.
            use_url_first (bool): Whether to try 'url' first for PDF.
            apply_barueri_hack (bool): Whether to apply Barueri-specific hack.

        Returns:
            requests.Response: The cancellation response.
        """
        # Check current status
        status_response = query_method(ref, record.company_id, record.nfse_environment)
        status_json = status_response.json()

        if status_response.status_code == 200:
            status = (
                status_json.get("status", "")
                if isinstance(status_json, dict)
                else status_json.get("status", "")
            )
            if (
                status == STATUS_CANCELADO
                and record.state_edoc != SITUACAO_EDOC_CANCELADA
            ):
                self._handle_cancelled_status(record, status_json, use_url_first)
                return status_response

        # Perform cancellation
        response = cancel_method(
            ref, record.cancel_reason, record.company_id, record.nfse_environment
        )
        json_data = response.json()

        if response.status_code in [200, 400]:
            code = json_data.get("codigo", "")
            status = json_data.get("status", "")

            if not code:
                code = json_data.get("erros", [{}])[0].get("codigo", "")
                if code == "OK200" or (not code and status == STATUS_CANCELADO):
                    code = CODE_NFE_CANCELADA

            if code == CODE_NFE_CANCELADA or status == STATUS_CANCELADO:
                # Query status again after cancellation
                status_rps = query_method(
                    ref, record.company_id, record.nfse_environment
                )
                status_json = status_rps.json()
                self._handle_cancelled_status(record, status_json, use_url_first)
                return response

            raise UserError(
                _(
                    "%(code)s - %(status)s",
                    code=code or response.status_code,
                    status=status,
                )
            )

        raise UserError(
            _(
                "%(code)s - %(msg)s",
                code=response.status_code,
                msg=json_data.get("mensagem", ""),
            )
        )

    def _process_cancel_municipal(self, record):
        """Process cancellation for NFSe Municipal."""
        ref = "rps" + record.rps_number
        nfse = record.env["focusnfe.nfse"]

        def query_method(ref, company, environment):
            return nfse.query_focus_nfse_by_rps(ref, 0, company, environment)

        def cancel_method(ref, cancel_reason, company, environment):
            return nfse.cancel_focus_nfse_document(
                ref, cancel_reason, company, environment
            )

        return self._process_cancel_base(
            record,
            ref,
            query_method,
            cancel_method,
            use_url_first=True,
            apply_barueri_hack=True,
        )

    def cancel_document_focus(self):
        """Cancel a NFSe document with the Focus NFSe provider.

        Parameters:
            None.

        Returns:
            The response regarding the cancellation request.
        """
        # Handle NFSe Municipal (original)
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_prescon_nacional
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
            json = response.json()

            if response.status_code == 202:
                if json["status"] == STATUS_PROCESSANDO_AUTORIZACAO:
                    if record.state == "rejeitada":
                        record.state_edoc = SITUACAO_EDOC_ENVIADA
                    else:
                        record._change_state(SITUACAO_EDOC_ENVIADA)
            elif response.status_code == 422:
                code = json.get("codigo", "")
                if code == CODE_NFE_AUTORIZADA and record.state in [
                    "a_enviar",
                    "enviada",
                    "rejeitada",
                ]:
                    record._document_status()
                else:
                    record._change_state(SITUACAO_EDOC_REJEITADA)
            else:
                record._change_state(SITUACAO_EDOC_REJEITADA)

    def _eletronic_document_send(self):
        """Send the electronic document to the NFSe provider.

        Parameters:
            None.

        Returns:
            None. Updates the document's status based on the response.
        """
        import pudb;pu.db
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
        return self.cancel_document_focus()

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
            self.search([("state", "in", ["enviada"])], limit=25)
            .filtered(filter_processador_edoc_nfse)
            .filtered(filter_prescon)
        )
        # Iterate over each record individually, as _document_status()
        # may expect a singleton in some cases
        for record in records:
            record._document_status()
