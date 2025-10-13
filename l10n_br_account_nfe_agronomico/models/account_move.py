
from odoo import models, _, api, fields
from odoo.exceptions import UserError
from odoo.addons.l10n_br_nfe_spec.models.v4_0.tipos_basico_v4_00 import (
    TUFEMI,
)

GUIATRANSITO_TPGUIA = [
    ("1", "GTA"),
    ("2", "TTA"),
    ("3", "DTA"),
    ("4", "ATV"),
    ("5", "PTV"),
    ("6", "GTV"),
    ("7", "Guia Florestal (DOF, SisFlora - PA e MT, SIAM - MG)"),
]

class AccountMove(models.Model):
    _inherit = "account.move"
    
    nfe40_guiaTransito = fields.Many2one(
        comodel_name="nfe.40.guiatransito",
        string='Agropecuária',
        copy=False,
    )


# class ResAgropecuario(models.Model):
#     _name = "res.agropecuario"
#     _description = "Documento Fiscal Agronômico"

#     # nfe40_guiaTransito = fields.Many2one(
#     #     comodel_name="res.guiatransito",
#     #     string="Agropecuario",
#     # )

#     nfe40_tpGuia = fields.Selection(
#         GUIATRANSITO_TPGUIA,
#         string="Tipo da Guia: 1 - GTA; 2 - TTA; 3",
#         help=(
#             "Tipo da Guia: 1 - GTA; 2 - TTA; 3 - DTA; 4 - ATV; 5 - PTV; 6 - "
#             "GTV; 7 - Guia Florestal (DOF, SisFlora - PA e MT, SIAM - MG)"
#         ),
#     )

#     nfe40_UFGuia = fields.Selection(
#         TUFEMI, string="UFGuia",
#     )

#     nfe40_serieGuia = fields.Char(string="Série da Guia")

#     nfe40_nGuia = fields.Char(string="Número da Guia")

class GuiaTransito(models.Model):    
    _name = "nfe.40.guiatransito"

    nfe40_tpGuia = fields.Selection(
        GUIATRANSITO_TPGUIA,
        string="Tipo da Guia: 1 - GTA; 2 - TTA; 3",
        help=(
            "Tipo da Guia: 1 - GTA; 2 - TTA; 3 - DTA; 4 - ATV; 5 - PTV; 6 - "
            "GTV; 7 - Guia Florestal (DOF, SisFlora - PA e MT, SIAM - MG)"
        ),
    )

    nfe40_UFGuia = fields.Selection(
        TUFEMI, string="UFGuia", 
    )

    nfe40_serieGuia = fields.Char(string="Série da Guia")

    nfe40_nGuia = fields.Char(string="Número da Guia")