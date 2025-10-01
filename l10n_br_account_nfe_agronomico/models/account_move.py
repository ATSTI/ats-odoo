
from odoo import models, _, api, fields
from odoo.exceptions import UserError

TUFEMI = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]

GUIATRANSITO_TPGUIA = [
    ("1", "GTA"),
    ("2", "TTA"),
    ("3", "DTA"),
    ("4", "ATV"),
    ("5", "PTV"),
    ("6", "GTV"),
    ("7", "Guia Florestal (DOF, SisFlora - PA e MT, SIAM - MG)"),
]

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # nfe40_guiaTransito = fields.Many2one(
    #     comodel_name="nfe.40.guiatransito",
    #     string='Agropecuária',
    #     copy=False,
    # )

    nfe40_defensivo = fields.One2many(
        "res.defensivo",
        "nfe_defensivo_agropecuario_id",
        string='Defensivo Agrícola',
        copy=False,
    )


class ResDefensivo(models.Model):
    _name = "res.defensivo"
    _description = "Documento Fiscal Agronômico - Defensivo Agrícola"

    nfe_defensivo_agropecuario_id = fields.Many2one(
        comodel_name="account.invoice", string="Documento Fiscal Agronômico",
    )
    nfe40_nReceituario = fields.Char(
        string="Número do Receituário ou Receita",
        help="Número do Receituário ou Receita do Defensivo / Agrotóxico",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Responsável Técnico",
    )

    nfe40_CPFRespTec = fields.Char(
        related="partner_id.cnpj_cpf",
        string="CPF",
        help="CPF do Responsável Técnico pelo receituário",
        store=True
    )


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
