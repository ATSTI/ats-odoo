# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentAgro(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if "nfe40_agropecuario" in class_obj._fields:
            agropecuario = self.env['nfe.40.agropecuario'].create({})
            self.nfe40_agropecuario = agropecuario
            if self.move_ids.guiatransp == True:
                guia_vals = {
                    "nfe40_tpGuia": self.move_ids.nfe40_tpGuia,
                    "nfe40_UFGuia": self.move_ids.nfe40_UFGuia,
                    "nfe40_serieGuia": self.move_ids.nfe40_serieGuia,
                    "nfe40_nGuia": self.move_ids.nfe40_nGuia,
                }
                guia = self.env["nfe.40.guiatransito"].create(guia_vals) 
                self.nfe40_agropecuario.nfe40_guiaTransito = guia
            else:
                self.nfe40_agropecuario = self.nfe40_agropecuario.nfe40_guiaTransito = False

        return super()._export_fields(xsd_fields, class_obj, export_dict)