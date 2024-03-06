# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FiscalDocumentTransp(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.transp":
            for tr in self.move_ids.trans_ids:
                vals_transp = {"nfe40_placa": tr.vehicle_id.plate,}
                obj_veic = self.env["nfe.40.tveiculo"].create(vals_transp).id
                self.nfe40_veicTransp = obj_veic
        return super()._export_fields(xsd_fields, class_obj, export_dict)
