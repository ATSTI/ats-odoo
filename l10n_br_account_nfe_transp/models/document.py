# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FiscalDocumentTransp(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.transp":
            for tr in self.move_ids.trans_ids:
                vals_vol = {
                    "nfe40_vol_transp_id": self.id,
                    "nfe40_qVol": tr.nfe40_qVol,
                    "nfe40_esp": tr.nfe40_esp,
                    "nfe40_marca": tr.nfe40_marca,
                    "nfe40_nVol": tr.nfe40_nVol,
                    "nfe40_pesoL": tr.nfe40_pesoL,
                    "nfe40_pesoB": tr.nfe40_pesoB,
                }
                obj_vol = self.env["nfe.40.vol"].search([('nfe40_vol_transp_id', '=', self.id)])
                if obj_vol:
                    obj_vol.write(vals_vol)
                vals_transp = {
                    "nfe40_placa": tr.vehicle_id.plate,
                    "nfe40_RNTC": tr.vehicle_id.rntc_code,
                    "nfe40_UF": tr.vehicle_id.state_id.code,
                }
                obj_veic = self.env["nfe.40.tveiculo"].create(vals_transp).id
                self.nfe40_veicTransp = obj_veic
                if not obj_vol:
                    self.env["nfe.40.vol"].create(vals_vol)
                    
        return super()._export_fields(xsd_fields, class_obj, export_dict)
