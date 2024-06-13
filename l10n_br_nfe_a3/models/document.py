# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
import re
import string
from datetime import datetime

from erpbrasil.base.fiscal import cnpj_cpf
from erpbrasil.base.fiscal.edoc import ChaveEdoc
from erpbrasil.edoc.pdf import base
from erpbrasil.transmissao import TransmissaoSOAP
from lxml import etree
from nfelib.nfe.bindings.v4_0.nfe_v4_00 import Nfe
from nfelib.nfe.ws.edoc_legacy import NFCeAdapter as edoc_nfce, NFeAdapter as edoc_nfe
from requests import Session


from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    EVENT_ENV_HML,
    EVENT_ENV_PROD,
    MODELO_FISCAL_NFCE,
    MODELO_FISCAL_NFE,
    PROCESSADOR_OCA,
)
from odoo.addons.spec_driven_model.models import spec_models

# from ..constants.nfe import (
#     NFCE_DANFE_LAYOUTS,
#     NFE_DANFE_LAYOUTS,
#     NFE_ENVIRONMENTS,
#     NFE_TRANSMISSIONS,
#     NFE_VERSIONS,
# )

PRODUCT_CODE_FISCAL_DOCUMENT_TYPES = ["55", "01"]

_logger = logging.getLogger(__name__)


def filter_processador_edoc_nfe(record):
    if record.processador_edoc == PROCESSADOR_OCA and record.document_type_id.code in [
        MODELO_FISCAL_NFE,
        MODELO_FISCAL_NFCE,
    ]:
        return True
    return False


class NFe(spec_models.StackedModel):
    _inherit = "l10n_br_fiscal.document"

    def _document_export(self, pretty_print=True):
        # result = super()._document_export()
        for record in self.filtered(filter_processador_edoc_nfe):
            edoc = record.serialize()[0]
            processador = record._processador()
            xml_file = processador.render_edoc_xsdata(edoc, pretty_print=pretty_print)[
                0
            ]
            _logger.debug(xml_file)
            event_id = self.event_ids.create_event_save_xml(
                company_id=self.company_id,
                environment=(
                    EVENT_ENV_PROD if self.nfe_environment == "1" else EVENT_ENV_HML
                ),
                event_type="0",
                xml_file=xml_file,
                document_id=self,
            )
            record.authorization_event_id = event_id
            if record.company_id.sudo().certificate_nfe_id or record.company_id.sudo().certificate_ecnpj_id:
                xml_assinado = processador.assina_raiz(edoc, edoc.infNFe.Id)
            else:
                xml_assinado = xml_file
            self._valida_xml(xml_assinado)
        # return result
