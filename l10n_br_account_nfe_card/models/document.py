# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentCard(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.pag":
            for crd in self.move_ids.card_ids:
                if self.nfe40_detPag.nfe40_tPag in ['03', '04', '17']:
                    card_vals = {
                        "nfe40_tpIntegra": '2', # 1 é com integração (POS, maquininhas) 2 é sem integração
                        "nfe40_CNPJ": punctuation_rm(crd.nfe40_CNPJ), # CNPJ da instituição de pagamento
                        "nfe40_tBand": crd.nfe40_tBand, # Bandeira do cartão 
                    }
                    if crd.nfe40_cAut:
                        card_vals["nfe40_cAut"] = crd.nfe40_cAut # Número de autorização da operação (n obrigatorio)
                    card = self.env["nfe.40.card"].create(card_vals)
                    self.nfe40_detPag.nfe40_card = card
                else:
                    continue

        return super()._export_fields(xsd_fields, class_obj, export_dict)
