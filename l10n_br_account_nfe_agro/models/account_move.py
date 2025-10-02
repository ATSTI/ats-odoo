
from odoo import models, _, fields


GUIATRANSITO_TPGUIA = [
    ("1", "GTA"),
    ("2", "TTA"),
    ("3", "DTA"),
    ("4", "ATV"),
    ("5", "PTV"),
    ("6", "GTV"),
    ("7", "Guia Florestal (DOF, SisFlora - PA e MT, SIAM - MG)"),
]

TUFEMI = [
    ("AC", "AC"),
    ("AL", "AL"),
    ("AM", "AM"),
    ("AP", "AP"),
    ("BA", "BA"),
    ("CE", "CE"),
    ("DF", "DF"),
    ("ES", "ES"),
    ("GO", "GO"),
    ("MA", "MA"),
    ("MG", "MG"),
    ("MS", "MS"),
    ("MT", "MT"),
    ("PA", "PA"),
    ("PB", "PB"),
    ("PE", "PE"),
    ("PI", "PI"),
    ("PR", "PR"),
    ("RJ", "RJ"),
    ("RN", "RN"),
    ("RO", "RO"),
    ("RR", "RR"),
    ("RS", "RS"),
    ("SC", "SC"),
    ("SE", "SE"),
    ("SP", "SP"),
    ("TO", "TO"),
]

class AccountMove(models.Model):
    _inherit = "account.move"
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}

    nfe40_tpGuia = fields.Selection(
        GUIATRANSITO_TPGUIA,
        string="Tipo da Guia: 1 - GTA; 2 - TTA; 3",
        xsd_required=True,
        help=(
            "Tipo da Guia: 1 - GTA; 2 - TTA; 3 - DTA; 4 - ATV; 5 - PTV; 6 - "
            "GTV; 7 - Guia Florestal (DOF, SisFlora - PA e MT, SIAM - MG)"
        ),
    )

    nfe40_UFGuia = fields.Selection(
        TUFEMI, string="UFGuia", xsd_required=True, xsd_type="TUfEmi"
    )

    nfe40_serieGuia = fields.Char(string="Série da Guia")

    nfe40_nGuia = fields.Char(string="Número da Guia", xsd_required=True)