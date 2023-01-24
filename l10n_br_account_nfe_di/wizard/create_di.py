# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

TPVIATRANSP_DI = [
    ("1", "1 - Maritima"),
    ("2", "2 - Fluvial"),
    ("3", "3 - Lacustre"),
    ("4", "4 - Aerea"),
    ("5", "5 - Postal"),
    ("6", "6 - Ferroviaria"),
    ("7", "7 - Rodoviaria"),
    ("8", "8 - Conduto/Rede Transmissão"),
    ("9", "9 - Meios Próprios"),
    ("10", "10 - Entrada/Saída Ficta"),
    ("11", "11 - Courier"),
    ("12", "12 - Em mãos"),
    ("13", "13 - Por reboque"),
    ]

TPINTERMEDIO_DI = [
        ("1", "1 - Por conta própria"),
        ("2", "2 - Por conta e ordem"),
        ("3", "3 - Encomenda"),
    ]

class WizardCreateDi(models.TransientModel):

    _name = "wizard.create.di"
    _description = "Faturar Contratos"
    
    state_clearance_id = fields.Many2one(
        comodel_name="res.country.state",
        string="State Clearance",
    )

    partner_acquirer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Parceiro",
    )

    nfe40_nDI = fields.Char(string="Numero DI")
    nfe40_dDI = fields.Date(string="Data DI")
    nfe40_cExportador = fields.Char(string="Cod. Exportador")
    nfe40_vAFRMM = fields.Float(string="Valor AFRMM")
    nfe40_xLocDesemb = fields.Char(string="Local Desembaraço")
    nfe40_dDesemb = fields.Date(string="Data Desembaraço")

    nfe40_UFDesemb = fields.Many2one('res.country.state', 'UF desembaraço',domain="[('country_id.code', '=', 'BR')]")

    nfe40_tpViaTransp = fields.Selection(
        selection=TPVIATRANSP_DI,
    )

    nfe40_tpIntermedio = fields.Selection(
        selection=TPINTERMEDIO_DI,
    )

    aml_id = fields.Many2one(
        comodel_name="account.move.line",
        string="AML"
    )

    nfe40_CNPJ = fields.Char(
        related="partner_acquirer_id.nfe40_CNPJ",
    )

    nfe40_UFTerceiro = fields.Many2one(
        'res.country.state', 'UF adquir./encomendante',
    )




    def action_create_di(self):
        # import wdb
        # wdb.set_trace()
        # ctx = self.env.context
        # aml = ctx.get("move_line")
        self.aml_id.di_ids = [(0, 0, {
                'name': self.nfe40_nDI,
                'aml_id': self.aml_id.id,
                'date_registration': self.nfe40_dDI,
                'state_id': self.nfe40_UFDesemb.id,
                'location': self.nfe40_xLocDesemb,
                'date_release': self.nfe40_dDesemb,
                'type_transportation': self.nfe40_tpViaTransp,
                'afrmm_value': self.nfe40_vAFRMM,
                'tpIntermedio': self.nfe40_tpIntermedio,
                'thirdparty_cnpj': self.nfe40_CNPJ,
                'thirdparty_state_id': self.nfe40_UFTerceiro.id,
                'exporting_code': self.nfe40_cExportador,
                'company_id': self.aml_id.company_id.id,
                # 'adi_ids': self.aml_id.id,

                # 'fiscal_operation_id': 14,
                # 'fiscal_operation_line_id': 26,
                # 'cfop_id': cfop_id.id if cfop_id else cfop_1949.id,
            })]

