# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WizardCreateDetexp(models.TransientModel):

    _name = "wizard.create.detexp"
    _description = "Detalhe da exportação"
    _rec_name = "nfe40_nDraw"

    nfe40_nDraw = fields.Char(
        string="Número do ato concessório de Drawback",
    )

    # nfe40_exportInd = fields.Many2one(
    #     "exp.ind",
    #     string="Exportação indireta",
    # )

    nfe40_nRE = fields.Char(
        string="Registro de exportação",
    )
    nfe40_chNFe = fields.Char(
        string="Chave de acesso da NF",
        help="Chave de acesso da NF-e recebida para exportação")
    nfe40_qExport = fields.Float(
        string="Quantidade do item efetivamente exportado",
    )
    am_id = fields.Many2one(
        comodel_name="account.move",
        string="Accoutn Move"
    )
    aml_id = fields.Many2one(
        comodel_name="account.move.line",
        domain=[('display_type', 'in', ('product', 'line_section', 'line_note'))],
        string="Produto",
        required=True,
    )

    # @api.onchange('nfe40_nDraw')
    # def onchange_nfe40_nDraw(self):
    #     ctx = self.env.context
    #     # exp = ctx.get("detexp_id")
    #     exp = ""
    #     exp_ids = ctx.get("exp")
    #     detexp_line = []
    #     if exp:
    #         detexp_line.append((0, 0, exp_ids))
    #         self.write({'nfe40_exportInd': detexp_line})

    def action_create_expind(self):
        detexp = self.env.context.get("detexp_id")
        # adi_line = []
        # adi = {}
        if detexp:
            if self.aml_id.move_id.state != "draft":
                raise UserError(_("Documento confirmado, alteração não permitida."))

            # if self.nfe40_exportInd:
            #     self.aml_id.exp_ids.exportind_ids.write(adi)
            #     expind = self.aml_id.exp_ids.exportind_ids
            # else:
            #     adi["registro_exp"] = line.nfe40_nRE
            #     adi["chava_nfe"] = line.nfe40_chNFe
            #     adi["q_export"] = line.nfe40_qExport
            #     expind = self.env["export.ind"].create(adi)

            self.aml_id.exp_ids = [(1, detexp, {
                'name': self.nfe40_nDraw,
                'aml_id': self.aml_id.id,
                'company_id': self.aml_id.company_id.id,
                'registro_exp': self.nfe40_nRE,
                'chava_nfe': self.nfe40_chNFe,
                'q_export': self.nfe40_qExport,
                })]
        else:
            # expind = False 
            # for line in self.nfe40_exportInd:
            #     adi["registro_exp"] = line.nfe40_nRE
            #     adi["chava_nfe"] = line.nfe40_chNFe
            #     adi["q_export"] = line.nfe40_qExport
            #     expind = self.env["export.ind"].create(adi).id

            self.aml_id.exp_ids = [(0, 0, {
                'name': self.nfe40_nDraw,
                'aml_id': self.aml_id.id,
                'company_id': self.aml_id.company_id.id,
                'registro_exp': self.nfe40_nRE,
                'chava_nfe': self.nfe40_chNFe,
                'q_export': self.nfe40_qExport,
                })]


# class ExpInd(models.TransientModel):
#     _name = "exp.ind"
#     _description = "Exportação indireta"
#     _rec_name = "nfe40_nRE"


