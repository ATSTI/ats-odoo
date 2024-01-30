# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging

from lxml import etree

from odoo import fields, models

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    LOTE_PROCESSADO,
    MODELO_FISCAL_NFCE,
    MODELO_FISCAL_NFE,
    PROCESSADOR_OCA,
    SITUACAO_EDOC_REJEITADA,
)

def filter_processador_edoc_nfe(record):
    if record.processador_edoc == PROCESSADOR_OCA and record.document_type_id.code in [
        MODELO_FISCAL_NFE,
        MODELO_FISCAL_NFCE,
    ]:
        return True
    return False


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"


    def _eletronic_document_send(self):
        for record in self.filtered(filter_processador_edoc_nfe):
            if self.xml_error_message:
                return
            processador = record._processador()
            for edoc in record.serialize():
                processo = None
                for p in processador.processar_documento(edoc):
                    processo = p
                    if processo.webservice == "nfeAutorizacaoLote":
                        record.authorization_event_id._save_event_file(
                            processo.envio_xml.decode("utf-8"), "xml"
                        )

            if processo.resposta.cStat in LOTE_PROCESSADO + ["100"]:
                if (hasattr(processo, 'protocolo')):
                    record.atualiza_status_nfe(processo)
                elif processo.resposta.cStat == "100" and not self.authorization_file_id:
                    # qdo a nota ja foi enviada, o primeiro retorno retConsSitNFe
                    # sera cStat = 100
                    arquivo = self.send_file_id
                    xml_string = base64.b64decode(arquivo.datas).decode()
                    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
                    try:
                        root = etree.fromstring(xml_string, parser=parser)
                    except:
                        # com a erpbrasil.edoc velha da erro acima
                        root = etree.fromstring(bytes(xml_string, encoding='utf-8'))
                    ns = {None: "http://www.portalfiscal.inf.br/nfe"}
                    new_root = etree.Element("nfeProc", nsmap=ns)

                    protNFe_node = etree.Element("protNFe")
                    infProt = etree.SubElement(protNFe_node, "infProt")
                    etree.SubElement(infProt, "tpAmb").text = processo.resposta.protNFe.infProt.tpAmb
                    etree.SubElement(infProt, "verAplic").text = processo.resposta.protNFe.infProt.verAplic
                    etree.SubElement(infProt, "dhRecbto").text = fields.Datetime.to_string(
                        processo.resposta.protNFe.infProt.dhRecbto)
                    protocol_date=fields.Datetime.to_string(
                        processo.resposta.protNFe.infProt.dhRecbto)
                    etree.SubElement(infProt, "nProt").text = processo.resposta.protNFe.infProt.nProt
                    # etree.SubElement(infProt, "digVal").text = processo.resposta.protNFe.infProt.digVal
                    etree.SubElement(infProt, "cStat").text = processo.resposta.protNFe.infProt.cStat
                    etree.SubElement(infProt, "xMotivo").text = processo.resposta.protNFe.infProt.xMotivo

                    new_root.append(root)
                    new_root.append(protNFe_node)
                    file = etree.tostring(new_root)
                    #record.atualiza_status_nfe(processo)
                    self.authorization_event_id.set_done(
                            status_code="100",
                            response="Autorizada",
                            protocol_date=protocol_date,
                            protocol_number=processo.resposta.protNFe.infProt.nProt,
                            file_response_xml=file.decode("utf-8"),
                        )
                    # state = "autorizada"

                    # record._change_state(state)

                    record.write(
                            {
                                "status_code": "100",
                                "status_name": "Autorizada",
                                "status_edoc": "autorizada",
                            }
                    )
                elif processo.resposta.cStat == "104" and not self.authorization_file_id:
                    # qdo a nota ja foi enviada, o primeiro retorno retConsSitNFe
                    # sera cStat = 100
                    arquivo = self.send_file_id
                    xml_string = base64.b64decode(arquivo.datas).decode()
                    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
                    try:
                        root = etree.fromstring(xml_string, parser=parser)
                    except:
                        # com a erpbrasil.edoc velha da erro acima
                        root = etree.fromstring(bytes(xml_string, encoding='utf-8'))
                    ns = {None: "http://www.portalfiscal.inf.br/nfe"}
                    new_root = etree.Element("nfeProc", nsmap=ns)

                    protNFe_node = etree.Element("protNFe")
                    infProt = etree.SubElement(protNFe_node, "infProt")
                    etree.SubElement(infProt, "tpAmb").text = processo.resposta.tpAmb
                    etree.SubElement(infProt, "verAplic").text = processo.resposta.verAplic
                    etree.SubElement(infProt, "dhRecbto").text = fields.Datetime.to_string(
                        processo.resposta.dhRecbto)
                    protocol_date=fields.Datetime.to_string(
                        processo.resposta.dhRecbto)
                    etree.SubElement(infProt, "nProt").text = processo.resposta.protNFe
                    # etree.SubElement(infProt, "digVal").text = processo.resposta.protNFe.infProt.digVal
                    etree.SubElement(infProt, "cStat").text = processo.resposta.cStat
                    etree.SubElement(infProt, "xMotivo").text = processo.resposta.xMotivo

                    new_root.append(root)
                    new_root.append(protNFe_node)
                    file = etree.tostring(new_root)
                    #record.atualiza_status_nfe(processo)
                    self.authorization_event_id.set_done(
                            status_code="100",
                            response="Autorizada",
                            protocol_date=protocol_date,
                            protocol_number=processo.resposta.protNFe,
                            file_response_xml=file.decode("utf-8"),
                        )
                    # state = "autorizada"

                    # record._change_state(state)

                    record.write(
                            {
                                "status_code": "100",
                                "status_name": "Autorizada",
                                "status_edoc": "autorizada",
                            }
                    )
            else:
                state = SITUACAO_EDOC_REJEITADA

                record._change_state(state)

                record.write(
                    {
                        "status_code": processo.resposta.cStat,
                        "status_name": processo.resposta.xMotivo,
                    }
                )
        return
