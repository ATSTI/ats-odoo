# Copyright 2019 Akretion (Raphaël Valyi <raphael.valyi@akretion.com>)
# Copyright 2019 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from erpbrasil.transmissao import TransmissaoSOAP
from erpbrasil.assinatura.excecoes import CertificadoExpirado
from nfelib.nfe.ws.edoc_legacy import NFCeAdapter as edoc_nfce
from nfelib.nfe.ws.edoc_legacy import NFeAdapter as edoc_nfe

from odoo import models
from odoo.exceptions import UserError  

from requests import Session

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

class NFe(models.Model):
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