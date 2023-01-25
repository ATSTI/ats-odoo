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
    _description = "Declaração de Importação (NT 2011/004)"
    
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

    nfe40_adi = fields.One2many(
        "di.adi",
        "DI_id",
        string="Adições (NT 2011/004)",
    )

    @api.onchange('nfe40_nDI')
    def onchange_nfe40_nDI(self):
        ctx = self.env.context
        di = ctx.get("di_id")
        adi_ids = ctx.get("adi")
        adi_line = []
        if di:
            adi_line.append((0, 0, adi_ids))
            self.write({'nfe40_adi': adi_line})

    def action_create_di(self):
        ctx = self.env.context
        di = ctx.get("di_id")
        adi_id = ctx.get("adi_id")
        adi_line = []
        adi = {}
        if di:
            for line_adi in self.nfe40_adi:
                adi["name"] = line_adi.nAdicao
                adi["sequence_di"] = line_adi.nSeqAdic
                adi["manufacturer_code"] = line_adi.cFabricante
                adi["amount_discount"] = line_adi.vDescDI
                adi["drawback_number"] = line_adi.nDraw
                adi_line.append((1, adi_id, adi))

            self.aml_id.di_ids = [(1, di, {
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
                    'adi_ids': adi_line,
                })]
        else:    
            for line in self.nfe40_adi:
                adi["name"] = line.nAdicao
                adi["sequence_di"] = line.nSeqAdic
                adi["manufacturer_code"] = line.cFabricante
                adi["amount_discount"] = line.vDescDI
                adi["drawback_number"] = line.nDraw
                adi_line.append((0, 0, adi))

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
                    'adi_ids': adi_line,
                })]


class DiAdi(models.TransientModel):

    _name = "di.adi"
    _description = "Adições (NT 2011/004)"

    brl_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moeda",
        compute="_compute_brl_currency_id",
        default=lambda self: self.env.ref('base.BRL').id,
    )

    def _compute_brl_currency_id(self):
        for item in self:
            item.brl_currency_id = self.env.ref("base.BRL").id

    DI_id = fields.Many2one("wizard.create.di")
    nAdicao = fields.Char(
        string="Número da Adição",
    )
    nSeqAdic = fields.Char(
        string="Número seqüencial do item dentro da Adição",
        required=True,
    )
    cFabricante = fields.Char(
        string="Código do fabricante estrangeiro",
        required=True,
        help="Código do fabricante estrangeiro (usado nos sistemas internos"
        "\nde informação do emitente da NF-e)"
    )
    vDescDI = fields.Monetary(
        currency_field="brl_currency_id",
        string="Valor do desconto do item da DI – adição",
    )
    nDraw = fields.Char(
        string="Número do ato concessório de Drawback",
    )

    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=lambda s: s.env.company)