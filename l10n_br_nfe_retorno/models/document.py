# Copyright 2019 Akretion (Raphaël Valyi <raphael.valyi@akretion.com>)
# Copyright 2019 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
import re
import string
from datetime import datetime
from io import StringIO
from unicodedata import normalize

from erpbrasil.assinatura import certificado as cert
from erpbrasil.base.fiscal.edoc import ChaveEdoc
from erpbrasil.edoc.nfe import NFe as edoc_nfe
from erpbrasil.edoc.pdf import base
from erpbrasil.transmissao import TransmissaoSOAP
from lxml import etree
from nfelib.v4_00 import leiauteNFe_sub as nfe_sub, retEnviNFe as leiauteNFe
from requests import Session

from odoo import _, api, fields
from odoo.exceptions import UserError, ValidationError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    LOTE_PROCESSADO,
    MODELO_FISCAL_NFCE,
    MODELO_FISCAL_NFE,
    PROCESSADOR_OCA,
    SITUACAO_EDOC_REJEITADA,
)
from odoo.addons.spec_driven_model.models import spec_models


_logger = logging.getLogger(__name__)


def filter_processador_edoc_nfe(record):
    if record.processador_edoc == PROCESSADOR_OCA and record.document_type_id.code in [
        MODELO_FISCAL_NFE,
        MODELO_FISCAL_NFCE,
    ]:
        return True
    return False


class NFe(spec_models.StackedModel):
    _name = "l10n_br_fiscal.document"
    _inherit = ["l10n_br_fiscal.document", "nfe.40.infnfe", "nfe.40.fat"]
    _stacked = "nfe.40.infnfe"
    _field_prefix = "nfe40_"
    _schema_name = "nfe"
    _schema_version = "4.0.0"
    _odoo_module = "l10n_br_nfe"
    _spec_module = "odoo.addons.l10n_br_nfe_spec.models.v4_0.leiaute_nfe_v4_00"
    _spec_tab_name = "NFe"
    _nfe_search_keys = ["nfe40_Id"]

    # all m2o at this level will be stacked even if not required:
    _force_stack_paths = (
        "infnfe.total",
        "infnfe.infAdic",
        "infnfe.exporta",
        "infnfe.cobr",
        "infnfe.cobr.fat",
    )

    def _eletronic_document_send(self):
        # super(NFe, self)._eletronic_document_send()
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
                    record.atualiza_status_nfe(
                        processo.protocolo.infProt, processo.processo_xml.decode("utf-8")
                    )
                elif processo.resposta.cStat == "100" and not self.authorization_file_id:
                    # qdo a nota ja foi enviada, o primeiro retorno retConsSitNFe
                    # sera cStat = 100
                    arquivo = self.send_file_id
                    xml_string = base64.b64decode(arquivo.datas).decode()
                    root = etree.fromstring(xml_string)
                    ns = {None: "http://www.portalfiscal.inf.br/nfe"}
                    new_root = etree.Element("nfeProc", nsmap=ns)

                    protNFe_node = etree.Element("protNFe")
                    infProt = etree.SubElement(protNFe_node, "infProt")
                    etree.SubElement(infProt, "tpAmb").text = processo.resposta.protNFe.infProt.tpAmb
                    etree.SubElement(infProt, "verAplic").text = processo.resposta.protNFe.infProt.verAplic
                    etree.SubElement(infProt, "dhRecbto").text = fields.Datetime.to_string(
                        processo.resposta.protNFe.infProt.dhRecbto)
                    etree.SubElement(infProt, "nProt").text = processo.resposta.protNFe.infProt.nProt
                    # etree.SubElement(infProt, "digVal").text = processo.resposta.protNFe.infProt.digVal
                    etree.SubElement(infProt, "cStat").text = processo.resposta.protNFe.infProt.cStat
                    etree.SubElement(infProt, "xMotivo").text = processo.resposta.protNFe.infProt.xMotivo

                    new_root.append(root)
                    new_root.append(protNFe_node)
                    file = etree.tostring(new_root)
                    record.atualiza_status_nfe(
                        processo.resposta.protNFe.infProt, file.decode("utf-8")
                    )
            elif not record.status_code and processo.resposta.cStat == "225":
                state = SITUACAO_EDOC_REJEITADA

                record._change_state(state)

                record.write(
                    {
                        "status_code": processo.resposta.cStat,
                        "status_name": processo.resposta.xMotivo,
                    }
                )
        return
