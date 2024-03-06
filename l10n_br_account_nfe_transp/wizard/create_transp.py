# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WizardCreateTransp(models.TransientModel):
    _name = "wizard.create.transp"
    _description = "Dados Transporte"

    carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        string="Carrier",
        ondelete="restrict",
    )

    nfe40_transporta = fields.Many2one(
        comodel_name="res.partner",
        related="carrier_id.partner_id",
        string="Dados do transportador",
    )

    incoterm_id = fields.Many2one(
        comodel_name="account.incoterms",
        string="Incoterm",
        help="International Commercial Terms are a series of"
        " predefined commercial terms used in international"
        " transactions.",
    )

    vehicle_id = fields.Many2one(
        comodel_name="l10n_br_delivery.carrier.vehicle",
        string="Veiculo",
    )

    am_id = fields.Many2one(
        comodel_name="account.move",
        string="Accoutn Move"
    )

    def action_create_transp(self):
        # import pudb;pu.db
        # am_id = self.env.context.get("default_am_id")
        # adi_line = []
        tr = {}
        # if am_id:
        if self.am_id.state != "draft":
            raise UserError(_("Documento confirmado, alteração não permitida."))

        tr["incoterm_id"] = self.incoterm_id.id
        if self.incoterm_id:
            self.am_id.invoice_incoterm_id = self.incoterm_id.id
            self.am_id.carrier_id = self.carrier_id.id
        tr["carrier_id"] = self.carrier_id.id
        tr["vehicle_id"] = self.vehicle_id.id
        tr["am_id"] = self.am_id.id
        self.env["transp.frete"].create(tr)
        # tr["carrier_id"] = self.carrier_id
        #     adi["chava_nfe"] = line.nfe40_chNFe
        #     adi["q_export"] = line.nfe40_qExport
        #     expind = self.env["export.ind"].create(adi)

        # self.aml_id.exp_ids = [(1, detexp, {
        #     'name': self.nfe40_nDraw,
        #     'aml_id': self.aml_id.id,
        #     'company_id': self.aml_id.company_id.id,
        #     'registro_exp': self.nfe40_nRE,
        #     'chava_nfe': self.nfe40_chNFe,
        #     'q_export': self.nfe40_qExport,
        #     })]
        # else:
        #     # expind = False 
        #     # for line in self.nfe40_exportInd:
        #     #     adi["registro_exp"] = line.nfe40_nRE
        #     #     adi["chava_nfe"] = line.nfe40_chNFe
        #     #     adi["q_export"] = line.nfe40_qExport
        #     #     expind = self.env["export.ind"].create(adi).id

        #     self.aml_id.exp_ids = [(0, 0, {
        #         'name': self.nfe40_nDraw,
        #         'aml_id': self.aml_id.id,
        #         'company_id': self.aml_id.company_id.id,
        #         'registro_exp': self.nfe40_nRE,
        #         'chava_nfe': self.nfe40_chNFe,
        #         'q_export': self.nfe40_qExport,
        #         })]


# class ExpInd(models.TransientModel):
#     _name = "exp.ind"
#     _description = "Exportação indireta"
#     _rec_name = "nfe40_nRE"


