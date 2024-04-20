# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FiscalDocumentTransp(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.icmstot":
            for tr in self.move_ids:
                if tr.amount_freight_value:
                    self.update({'nfe40_vFrete': tr.amount_freight_value})
                if tr.amount_insurance_value:
                    self.update({'nfe40_vSeg': tr.amount_insurance_value})
                if tr.amount_other_value:
                    self.update({'nfe40_vOutro': tr.amount_other_value})

        return super()._export_fields(xsd_fields, class_obj, export_dict)
