
from odoo import models, _, api, fields
from odoo.exceptions import UserError

IBSCBSALIQ_CST = [
    (
        "000",
        (
            "Operação Tributável - Base de Cálculo = Valor da Operação Alíquota "
            "Normal (Cumulativo/Não Cumulativo)"
        ),
    ),
    (
        "002",
        (
            "Operação Tributável - Base de Calculo = Valor da Operação (Alíquota "
            "Diferenciada)"
        ),
    ),
]

class AccountMove(models.Model):
    _inherit = "account.move"
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    
    ibscbs = fields.Boolean('IBSCBS')

    cst_ibscbs = fields.Selection(IBSCBSALIQ_CST, string='Garantia do Comprador', default='000')