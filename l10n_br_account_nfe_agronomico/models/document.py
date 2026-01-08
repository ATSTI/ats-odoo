# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class FiscalDocumentAgro(models.Model):
    _inherit = "l10n_br_fiscal.document"
    ##########################
    # NF-e tag: AGROPECUÁRIO
    ##########################

    nfe40_guiaTransito = fields.Many2one(
        comodel_name="nfe.40.guiatransito",
        string="Agropecuario",
    )

    # def _export_fields(self, xsd_fields, class_obj, export_dict):
    #     if class_obj._name == "nfe.40.pag":
    #         for agro in self.move_ids.nfe40_guiaTransito:
    #             agro_vals = {
    #                 "nfe40_tpGuia": agro.nfe40_tpGuia, # Tipo da Guia: 1 - GTA; 2 - TTA; 3 - DTA; 4 - ATV; 5 - PTV; 6 - GTV; 7 - Guia Florestal (DOF, SisFlora - PA e MT, SIAM - MG)
    #                 "nfe40_UFGuia": agro.nfe40_UFGuia, # Sigla da UF do órgão de emissão da guia 
    #                 "nfe40_serieGuia": agro.nfe40_serieGuia, # Série da Guia
    #                 "nfe40_nGuia": agro.nfe40_nGuia, # Número da Guia
    #             }
    #             agr = self.env["nfe.40.guiatransito"].create(agro_vals)
    #             # self.nfe40_agropecuario = agr.id

    #     return super()._export_fields(xsd_fields, class_obj, export_dict)
