# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
import base64
from lxml import etree
from datetime import datetime
from odoo import _, models, api
from odoo.exceptions import UserError
from requests import Session
from erpbrasil.transmissao import TransmissaoSOAP
from erpbrasil.assinatura import certificado as cert
from erpbrasil.edoc.nfe import NFe


class DocumentStatusWizard(models.TransientModel):
    _inherit = "l10n_br_fiscal.document.status.wizard"
    
    @api.model
    def _get_certificate(self):
        certificate_id = self.document_id.company_id.certificate_nfe_id
        return cert.Certificado(
            arquivo=certificate_id.file,
            senha=certificate_id.password,
        )
    
    def get_document_status(self):
        self.document_id.ensure_one()
        session = Session()
        session.verify = False
        nfe = NFe(
            TransmissaoSOAP(self._get_certificate(), session),
            self.document_id.company_id.state_id.ibge_code,
            versao=self.document_id.nfe_version,
            ambiente=self.document_id.nfe_environment,
        )

        if self.document_id.authorization_protocol:
            raise UserError(_("Authorization Protocol Not Found!"))
        if self.document_id.status_description and 'nRec' in self.document_id.status_description:
            msg = self.document_id.status_description
            recibo = msg[msg.find('nRec')+5:]
            recibo = re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ: ]', '', recibo)
            evento = nfe.consulta_recibo(recibo)
            if evento.resposta.cStat != '104':
                msg = f"Retorno: {str(evento.resposta.cStat)}-{evento.resposta.xMotivo}!"
                raise UserError(_(msg))
            prot = evento.resposta.protNFe
            protocolo = prot[0].infProt.nProt
            for p_id in prot:
                p = p_id.infProt
                # protocolo = p.nProt
                # chave = p.chNFe
                data_rec = datetime.fromisoformat(p.dhRecbto)
                # dig_val = p.digVal
                if protocolo:
                    arquivo = self.document_id.send_file_id
                    xml_string = base64.b64decode(arquivo.datas).decode()
                    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
                    try:
                        root = etree.fromstring(xml_string, parser=parser)
                    except:
                        # com a erpbrasil.edoc velha da erro acima
                        root = etree.fromstring(bytes(xml_string, encoding='utf-8'))
                    ns = {None: "http://www.portalfiscal.inf.br/nfe"}
                    new_root = etree.Element("nfeProc", nsmap=ns)
                    #print (etree.tostring(processo.resposta, pretty_print=True))
                    protNFe_node = etree.Element("protNFe")
                    infProt = etree.SubElement(protNFe_node, "infProt")
                    etree.SubElement(infProt, "tpAmb").text = p.tpAmb
                    etree.SubElement(infProt, "verAplic").text = p.verAplic
                    etree.SubElement(infProt, "dhRecbto").text = p.dhRecbto
                    etree.SubElement(infProt, "nProt").text = p.nProt
                    etree.SubElement(infProt, "cStat").text = p.cStat
                    etree.SubElement(infProt, "xMotivo").text = p.xMotivo

                    new_root.append(root)
                    new_root.append(protNFe_node)
                    file = etree.tostring(new_root)
                    self.document_id.authorization_event_id.set_done(
                            status_code="100",
                            response="Autorizada",
                            protocol_date=data_rec.strftime('%Y-%m-%d %H:%M:%S'),
                            protocol_number=p.nProt,
                            file_response_xml=file.decode("utf-8"),
                        )
                    self.document_id.write(
                            {
                                "status_code": "100",
                                "status_name": "Autorizada",
                                "state_edoc": "autorizada",
                            }
                    )
