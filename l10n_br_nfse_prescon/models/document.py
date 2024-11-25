# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime

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

REQ_HEADERS = {
    'Name': 'NFSe - Prescon Informatica',
    'Content-Type': 'text/xml; charset=utf-8',
    'Accept': 'application/soap+xml, application/dime, multipart/related, text/*',
    'SOAPAction': 'wsdl#ACTION',
    'Binding': 'NFSe - Prescon InformaticaBinding',
    'Endpoint': 'wsdl',
    'Style': 'rpc',
}

REQ_BODY = "<?xml version=\"1.0\"?>"
REQ_BODY += "<soap:Envelope xmlns:soap=\"https://www.w3.org/2003/05/soap-envelope\">"
REQ_BODY += "<soap:Header></soap:Header>"
REQ_BODY += "<soap:Body>"
REQ_BODY += "str_Body"
REQ_BODY += "</soap:Body>"
REQ_BODY += "</soap:Envelope>"

TIMEOUT = 60  # 60 seconds

_logger = logging.getLogger(__name__)


def filter_presconnfe(record):
    return record.company_id.provedor_nfse == "presconnfe"


class PresconnfeNfse(models.AbstractModel):
    _name = "presconnfe.nfse"
    _description = "Prescon NFSE"

    def getToken_prescon(self, company):
        if company.presconnfe_production_token:
            tempo_token = (datetime.now() - company.presconnfe_nfse_token_validate).total_seconds()
            if (tempo_token/60) < 15:
                return company.presconnfe_production_token
        req_headers = REQ_HEADERS
        req_headers["SOAPAction"] = f"{company.presconnfe_nfse_wsdl}#getToken"
        req_headers["Endpoint"] = company.presconnfe_nfse_wsdl
        body = "<m:getTokenRequest>"
        body += f"<m:strInscricaoMunicipal>{company.inscr_mun}</m:strInscricaoMunicipal>"
        body += f"<m:strSenha>{company.presconnfe_nfse_password}</m:strSenha>"
        body += "</m:getTokenRequest>"
        req_body = REQ_BODY.replace("str_Body", body)
        wsdl = f"{company.presconnfe_nfse_wsdl}?wsdl"
        response = requests.post(
            wsdl,
            data=req_body,
            headers=req_headers,
        )
        if response.status_code == 500:
            root = ET.fromstring(response.text)
            retorno = [e.text for e in root.findall('.//retorno')]
            company.presconnfe_production_token = retorno[0]
            company.presconnfe_nfse_token_validate = datetime.now()
            return retorno[0]
        return False

    def _make_prescon_nfse_http_request(self, company, method, token, data=None):
        req_headers = REQ_HEADERS
        req_headers["SOAPAction"] = f"{company.presconnfe_nfse_wsdl}#{method}"
        req_headers["Endpoint"] = company.presconnfe_nfse_wsdl
        body = ""
        if method == "strJsonInvoice":
            body = "<m:setInvoiceRequest>"
            body += f"<m:strJsonInvoice>{data}</m:strJsonInvoice>"
            body += f"<m:strToken>{token}</m:strToken>"
            body += "</m:setInvoiceRequest>"
        req_body = REQ_BODY.replace("str_Body", body)
        wsdl = f"{company.presconnfe_nfse_wsdl}?wsdl"
        try:
            response = requests.post(
                wsdl,
                data=req_body,
                headers=req_headers,
            )
            if response.status_code == 500:
                root = ET.fromstring(response.text)
                retorno = [e.text for e in root.findall('.//retorno')]
            return retorno[0]
        except requests.HTTPError as e:
            raise UserError(_("Error communicating with NFSe service: %s") % e) from e

    # def _identify_service_recipient(self, recipient):
    #     """Identify whether the service recipient is a CPF or CNPJ.

    #     Args:
    #         recipient (dict): A dictionary containing either 'cpf' or 'cnpj' keys.

    #     Returns:
    #         dict: A dictionary with either a 'cpf' or 'cnpj' key and its value.
    #     """
    #     return (
    #         {"cpf": recipient.get("cpf")}
    #         if recipient.get("cpf")
    #         else {"cnpj": recipient.get("cnpj")}
    #     )

    @api.model
    def process_prescon_nfse_document(self, edoc, company):
        token = self.getToken_prescon(company)
        data = self._prepare_payload(*edoc, company)
        payload = json.dumps(data)
        return self._make_prescon_nfse_http_request(
            company, "strJsonInvoice", token, data=payload
        )

    def _prepare_payload(self, rps, service, recipient, company):
        rps_info = rps.get("rps")
        service = service.get("service")
        recipient = recipient.get("recipient")
        # recipient_identification = self._identify_service_recipient(recipient)
        if recipient.get("cnpj"):
            tipoTomador = "J"
            documento = recipient.get("cnpj")
        if recipient.get("cpf"):
            tipoTomador = "F"
            documento = recipient.get("cpf")
        str_invoice = [{
            "im": company.inscr_mun,
            "NumeroNota": rps_info.get("numero"),
            "DataEmissao": rps_info.get("data_emissao")[:10],
            "NomeTomador": recipient.get("razao_social"),
            "tipoDocTomador": tipoTomador,
            "documentoTomador": documento,
            "InscricaoEstadualTomador": recipient.get("inscricao_estadual") or "",
            "logradouroTomador": recipient.get("endereco"),
            "numeroTomador": recipient.get("numero"),
            "complementoTomador": "",
            "bairroTomador": recipient.get("bairro"),
            "cidadeTomador": recipient.get("municipio"),
            "ufTomador": recipient.get("uf"),
            "PAISTomador": "BRASIL",
            "emailTomador": recipient.get("email"),
            "logradouroServico": recipient.get("endereco"),
            "CEPTomador": recipient.get("cep"),
            "numeroServico": recipient.get("numero"),
            "complementoServico": "",
            "bairroServico": recipient.get("bairro"),
            "cidadeServico": recipient.get("municipio"),
            "ufServico": recipient.get("uf"),
            "issRetido": service.get("iss_retido"),
            "devidoNoLocal": 0,
            "observacao": "",
            "INSS": round(service.get("valor_inss", 0), 2),
            "IRPJ": round(service.get("valor_ir", 0), 2),
            "CSLL": round(service.get("valor_csll", 0), 2),
            "COFINS": round(service.get("valor_cofins", 0), 2),
            "PISPASEP": round(service.get("valor_pis", 0), 2),
            "CEPServico": recipient.get("cep"),
            "PAISServico": "BRASIL",
            "descricao": service.get("discriminacao"),
            "atividade": service.get(company.presconnfe_nfse_service_type_value),
            "valor": round(service.get("valor_servicos", 0), 2),
            "aliquota": service.get("aliquota"),
            "deducaoMaterial": round(service.get("valor_deducoes", 0), 2),
            "descontoCondicional": round(service.get("desconto_condicionado", 0), 2),
            "descontoIncondicional": round(
                service.get("desconto_incondicionado", 0), 2
            ),
            "valorDeducao": round(service.get("valor_deducoes", 0), 2),
            "baseCalculo": round(service.get("base_calculo", 0), 2),
            "valorIss": round(service.get("valor_iss", 0), 2),
            "valorTotalNota": round(service.get("valor_liquido_nfse", 0), 2),
            "tipoEnquadramento": "N",
            "tipoIss": "M",
            "hashMd5": ""            
        }]
        return str_invoice

    # def _prepare_provider_data(self, rps, company):
    #     """Construct the provider section of the payload.

    #     Args:
    #         rps (dict): Information about the RPS.
    #         company (recordset): The company record.

    #     Returns:
    #         dict: The provider section of the payload.
    #     """
    #     return {
    #         "cnpj": rps.get("cnpj"),
    #         "inscricao_municipal": rps.get("inscricao_municipal"),
    #         "codigo_municipio": company.city_id.ibge_code,
    #     }

    # def _prepare_service_data(self, service, company):
    #     """Construct the service section of the payload.

    #     Args:
    #         service (dict): Details of the service provided.
    #         company (recordset): The company record.

    #     Returns:
    #         dict: The service section of the payload.
    #     """
    #     return {
    #         "aliquota": service.get("aliquota"),
    #         "base_calculo": round(service.get("base_calculo", 0), 2),
    #         "discriminacao": service.get("discriminacao"),
    #         "iss_retido": service.get("iss_retido"),
    #         "codigo_municipio": service.get("municipio_prestacao_servico"),
    #         "item_lista_servico": service.get(company.presconnfe_nfse_service_type_value),
    #         "codigo_cnae": service.get(company.presconnfe_nfse_cnae_code_value),
    #         "valor_iss": round(service.get("valor_iss", 0), 2),
    #         "valor_iss_retido": round(service.get("valor_iss_retido", 0), 2),
    #         "valor_pis": round(service.get("valor_pis", 0), 2),
    #         "valor_cofins": round(service.get("valor_cofins", 0), 2),
    #         "valor_inss": round(service.get("valor_inss", 0), 2),
    #         "valor_ir": round(service.get("valor_ir", 0), 2),
    #         "valor_csll": round(service.get("valor_csll", 0), 2),
    #         "valor_deducoes": round(service.get("valor_deducoes", 0), 2),
    #         "fonte_total_tributos": service.get("fonte_total_tributos", "IBPT"),
    #         "desconto_incondicionado": round(
    #             service.get("desconto_incondicionado", 0), 2
    #         ),
    #         "desconto_condicionado": round(service.get("desconto_condicionado", 0), 2),
    #         "outras_retencoes": round(service.get("outras_retencoes", 0), 2),
    #         "valor_servicos": round(service.get("valor_servicos", 0), 2),
    #         "valor_liquido": round(service.get("valor_liquido_nfse", 0), 2),
    #         "codigo_tributario_municipio": service.get("codigo_tributacao_municipio"),
    #     }

    # def _prepare_recipient_data(self, recipient, identification):
    #     """Construct the recipient section of the payload.

    #     Args:
    #         recipient (dict): Information about the service recipient.
    #         identification (dict): The recipient's identification (CPF or CNPJ).

    #     Returns:
    #         dict: The recipient section of the payload.
    #     """
    #     return {
    #         **identification,
    #         "razao_social": recipient.get("razao_social"),
    #         "email": recipient.get("email"),
    #         "endereco": {
    #             "bairro": recipient.get("bairro"),
    #             "cep": recipient.get("cep"),
    #             "codigo_municipio": recipient.get("codigo_municipio"),
    #             "logradouro": recipient.get("endereco"),
    #             "numero": recipient.get("numero"),
    #             "uf": recipient.get("uf"),
    #         },
    #     }

    # @api.model
    # def query_prescon_nfse_by_rps(self, ref, complete, company, environment):
    #     """Query NFSe by RPS.

    #     Args:
    #         ref (str): The RPS reference.
    #         complete (bool): Whether to return complete information.
    #         company (recordset): The company record.

    #     Returns:
    #         requests.Response: The response from the NFSe service.
    #     """
    #     token = company.getToken_prescon()
    #     # url = f"{NFSE_URL[environment]}{API_ENDPOINT['status']}{ref}"
    #     return self._make_prescon_nfse_http_request(
    #         "GET",  token, params={"completa": complete}
    #     )

    @api.model
    def cancel_prescon_nfse_document(self, ref, cancel_reason, company, environment):
        """Cancel an electronic fiscal document.

        Args:
            ref (str): The document reference.
            cancel_reason (str): The reason for cancellation.
            company (recordset): The company record.

        Returns:
            requests.Response: The response from the NFSe service.
        """
        token = self.getToken_prescon()
        data = {"justificativa": cancel_reason}

        return self._make_prescon_nfse_http_request(
            company, "DELETE", token, data=json.dumps(data)
        )


class Document(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def make_prescon_nfse_pdf(self, content):
        """Generate a PDF for a NFSe document using prescon NFSe service.

        Parameters:
            - content: The binary content of the PDF to be attached.

        Returns:
            None. Creates or updates an 'ir.attachment' record with the PDF content.
        """
        if not self.filtered(filter_processador_edoc_nfse).filtered(filter_presconnfe):
            return super().make_pdf()
        else:
            if self.document_number:
                filename = "NFS-e-" + self.document_number + ".pdf"
            # else:
            #     filename = "RPS-" + self.rps_number + ".pdf"

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

    def _serialize(self, edocs):
        """Serialize electronic documents (edocs) for sending to the NFSe provider.

        Parameters:
            - edocs: The initial list of electronic documents to serialize.

        Returns:
            The updated list of serialized electronic documents, including additional
            NFSe-specific information.
        """
        edocs = super()._serialize(edocs)
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_presconnfe
        ):
            edoc = []
            edoc.append({"rps": record._prepare_lote_rps()})
            edoc.append({"service": record._prepare_dados_servico()})
            edoc.append({"recipient": record._prepare_dados_tomador()})
            edocs.append(edoc)
        return edocs

    def _document_export(self, pretty_print=True):
        """Prepare and export the document's electronic information.

        Parameters:
            - pretty_print: A boolean indicating whether the exported data should be
            formatted for readability.

        Returns:
            The result of the document export operation.
        """
        if self.filtered(filter_processador_edoc_nfse).filtered(filter_presconnfe):
            result = super(FiscalDocument, self)._document_export()
        else:
            result = super()._document_export()
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_presconnfe
        ):
            event_id = record.event_ids.create_event_save_xml(
                company_id=self.company_id,
                environment=(
                    EVENT_ENV_PROD if record.nfse_environment == "1" else EVENT_ENV_HML
                ),
                event_type="0",
                xml_file="",
                document_id=record,
            )
            record.authorization_event_id = event_id
        return result

    def _document_status(self):
        """Check and update the status of the NFSe document.

        Parameters:
            None.

        Returns:
            A string indicating the current status of the document.
        """
        result = super()._document_status()
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_presconnfe
        ):
            # ref = "rps" + record.rps_number
            # response = self.env["presconnfe.nfse"].query_prescon_nfse_by_rps(
            #     ref, 0, record.company_id, record.nfse_environment
            # )

            # json = response.json()

            # if response.status_code == 200:
            #     if record.state in ["a_enviar", "enviada", "rejeitada"]:
            #         if json["status"] == "autorizado":
            #             aware_datetime = datetime.strptime(
            #                 json["data_emissao"], "%Y-%m-%dT%H:%M:%S%z"
            #             )
            #             utc_datetime = aware_datetime.astimezone(pytz.utc)
            #             naive_datetime = utc_datetime.replace(tzinfo=None)
            #             record.write(
            #                 {
            #                     "verify_code": json["codigo_verificacao"],
            #                     "document_number": json["numero"],
            #                     "authorization_date": naive_datetime,
            #                 }
            #             )

            #             xml = requests.get(
            #                 NFSE_URL[record.nfse_environment]
            #                 + json["caminho_xml_nota_fiscal"],
            #                 timeout=TIMEOUT,
            #             ).content.decode("utf-8")
            #             pdf_content = (
            #                 requests.get(
            #                     json["url"],
            #                     timeout=TIMEOUT,
            #                     verify=record.company_id.nfse_ssl_verify,
            #                 ).content
            #                 or requests.get(
            #                     json["url_danfse"],
            #                     timeout=TIMEOUT,
            #                     verify=record.company_id.nfse_ssl_verify,
            #                 ).content
            #             )

            #             # record.make_prescon_nfse_pdf(pdf_content)

            #             if not record.authorization_event_id:
            #                 record._document_export()

            #             if record.authorization_event_id:
            #                 record.authorization_event_id.set_done(
            #                     status_code=4,
            #                     response=_("Processado com Sucesso"),
            #                     protocol_date=record.authorization_date,
            #                     protocol_number=record.authorization_protocol,
            #                     file_response_xml=xml,
            #                 )
            #                 record._change_state(SITUACAO_EDOC_AUTORIZADA)

            #         elif json["status"] == "erro_autorizacao":
            #             record.write(
            #                 {
            #                     "edoc_error_message": json["erros"][0]["mensagem"],
            #                 }
            #             )
            #             record._change_state(SITUACAO_EDOC_REJEITADA)
            #         elif json["status"] == "cancelado":
            #             record._change_state(SITUACAO_EDOC_CANCELADA)

            #     result = _(json["status"])
            result = "Unable to retrieve the document status."
        return result

    def cancel_document_prescon(self):
        """Cancel a NFSe document with the prescon NFSe provider.

        Parameters:
            None.

        Returns:
            The response regarding the cancellation request.
        """
        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_presconnfe
        ):
            raise UserError(
                        _(
                            "Ação não implementada",
                        )
            )
            ref = "rps" + record.rps_number
            response = self.env["presconnfe.nfse"].cancel_prescon_nfse_document(
                ref, record.cancel_reason, record.company_id, record.nfse_environment
            )

            code = False
            status = False

            json = response.json()

            if response.status_code in [200, 400]:
                try:
                    code = json["codigo"]
                    response = True
                except Exception:
                    _logger.error(
                        _("HTTP status is 200 or 400 but unable to read json['codigo']")
                    )
                try:
                    status = json["status"]
                except Exception:
                    _logger.error(
                        _("HTTP status is 200 or 400 but unable to read json['status']")
                    )

                # hack barueri - provisório
                if not code and record.company_id.city_id.ibge_code == "3505708":
                    try:
                        code = json["erros"][0].get("codigo")
                    except Exception:
                        _logger.error(
                            _("HTTP status is 200 or 400 but unable to read error code")
                        )
                    if code == "OK200":
                        code = "nfe_cancelada"

                if code == "nfe_cancelada" or status == "cancelado":
                    record.cancel_event_id = record.event_ids.create_event_save_xml(
                        company_id=record.company_id,
                        environment=(
                            EVENT_ENV_PROD
                            if record.nfse_environment == "1"
                            else EVENT_ENV_HML
                        ),
                        event_type="2",
                        xml_file="",
                        document_id=record,
                    )

                    record.cancel_event_id.set_done(
                        status_code=4,
                        response=_("Processado com Sucesso"),
                        protocol_date=fields.Datetime.to_string(fields.Datetime.now()),
                        protocol_number="",
                        file_response_xml="",
                    )

                    status_rps = self.env["presconnfe.nfse"].query_prescon_nfse_by_rps(
                        ref, 0, record.company_id, record.nfse_environment
                    )
                    status_json = status_rps.json()
                    pdf_content = (
                        requests.get(
                            status_json["url"],
                            timeout=TIMEOUT,
                            verify=record.company_id.nfse_ssl_verify,
                        ).content
                        or requests.get(
                            status_json["url_danfse"],
                            timeout=TIMEOUT,
                            verify=record.company_id.nfse_ssl_verify,
                        ).content
                    )
                    record.make_prescon_nfse_pdf(pdf_content)

                    return response

                else:
                    raise UserError(
                        _(
                            "%(code)s - %(status)s",
                            code=response.status_code,
                            status=status,
                        )
                    )
            else:
                raise UserError(
                    _(
                        "%(code)s - %(msg)s",
                        code=response.status_code,
                        msg=json["mensagem"],
                    )
                )

    def _eletronic_document_send(self):
        """Send the electronic document to the NFSe provider.

        Parameters:
            None.

        Returns:
            None. Updates the document's status based on the response.
        """
        res = super()._eletronic_document_send()

        for record in self.filtered(filter_processador_edoc_nfse).filtered(
            filter_presconnfe
        ):
            for edoc in record.serialize():
                response = self.env["presconnfe.nfse"].process_prescon_nfse_document(
                    edoc, record.company_id
                )
                if "Sucesso" in response:
                    vals = dict()
                    record._change_state(SITUACAO_EDOC_AUTORIZADA)
                    vals["authorization_date"] = datetime.now()
                    vals["status_code"] = 4
                    vals["edoc_error_message"] = ""
                    vals["status_name"] = _(response)
                    vals["document_number"] = record.rps_number
                    vals["verify_code"] = response[response.find('|')+2:]
                    record.write(vals)
                else:
                    record.edoc_error_message = response
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
            .filtered(filter_presconnfe)
        )
        if records:
            records._document_status()
