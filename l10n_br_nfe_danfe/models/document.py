# Copyright 2019 Akretion (Raphaël Valyi <raphael.valyi@akretion.com>)
# Copyright 2019 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz
import base64
import io

from odoo import _, models

from ..models.danfe import danfe
from lxml import etree

from odoo import _

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFCE,
    MODELO_FISCAL_NFE,
    PROCESSADOR_OCA,
)

def filter_processador_edoc_nfe(record):
    if record.processador_edoc == PROCESSADOR_OCA and record.document_type_id.code in [
        MODELO_FISCAL_NFE,
        MODELO_FISCAL_NFCE,
    ]:
        return True
    return False

class DocumentNfe(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def make_pdf(self):
        if not self.filtered(filter_processador_edoc_nfe):
            return super().make_pdf()

        file_pdf = self.file_report_id
        self.file_report_id = False
        file_pdf.unlink()

        if self.authorization_file_id:
            arquivo = self.authorization_file_id
            xml_string = base64.b64decode(arquivo.datas)
        else:
            arquivo = self.send_file_id
            xml_string = base64.b64decode(arquivo.datas)
            xml_string = self.temp_xml_autorizacao(xml_string)

        # Teste Usando impressao via ReportLab Pytrustnfe
        evento_xml = []
        cce_list = self.env['l10n_br_fiscal.event'].search([
            ('type', '=', '14'),
            ('document_id', '=', self.id),
        ])

        if cce_list:
            for cce in cce_list:
                cce_xml = base64.b64decode(cce.file_request_id.datas)
                evento_xml.append(etree.fromstring(cce_xml))

        logo = base64.b64decode(self.company_id.logo)

        tmpLogo = io.BytesIO()
        tmpLogo.write(logo)
        tmpLogo.seek(0)

        timezone = pytz.timezone(self.env.context.get('tz') or 'UTC')
        xml_element = etree.fromstring(xml_string)

        cancel_list = self.env['l10n_br_fiscal.event'].search([
            ('type', '=', '2'),
            ('document_id', '=', self.id),
        ])
        if cancel_list:
            cancel_xml = base64.b64decode(cancel_list.file_request_id.datas).decode()
            evento_xml.append(etree.fromstring(cancel_xml))

        oDanfe = danfe(list_xml=[xml_element], logo=tmpLogo,
            evento_xml=evento_xml, timezone=timezone)
        tmpDanfe = io.BytesIO()
        oDanfe.writeto_pdf(tmpDanfe)
        danfe_file = tmpDanfe.getvalue()
        tmpDanfe.close()

        # base64.b64encode(bytes(tmpDanfe)),

        self.file_report_id = self.env["ir.attachment"].create(
            {
                "name": self.document_key + ".pdf",
                "res_model": self._name,
                "res_id": self.id,
                "datas": base64.b64encode(danfe_file),
                "mimetype": "application/pdf",
                "type": "binary",
            }
        )
