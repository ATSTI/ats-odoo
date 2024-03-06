
from odoo import models, _, api, fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
    trans_ids = fields.One2many(
        "transp.frete",
        "am_id",
        # compute="_compute_di_ids",
        string='Transportadora',
    )

    # @api.depends("invoice_line_ids")
    # def _compute_di_ids(self):
    #     di_ids = self.env["declaracao.importacao"].search([
    #         ("aml_id", "in", self.invoice_line_ids._ids)
    #     ])
    #     for record in self:
    #         record.di_ids = di_ids

    def button_wizard_transp(self):
        for move in self:
            ctx = {
                'default_am_id': move.id,
            }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.create.transp',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class TranspFrete(models.Model):
    _name = "transp.frete"
    _description = "Detalhe da Transportadora"

    incoterm_id = fields.Many2one(
        comodel_name="account.incoterms",
        string="Tipo de Frete",
        help="International Commercial Terms are a series of"
        " predefined commercial terms used in international"
        " transactions.",
    )

    carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        string="Veículo",
        ondelete="restrict",
    )

    nfe40_transporta = fields.Many2one(
        comodel_name="res.partner",
        related="carrier_id.partner_id",
        string="Dados do transportador",
    )

    vehicle_id = fields.Many2one(
        comodel_name="l10n_br_delivery.carrier.vehicle",
        string="Veiculo",
    )
    am_id = fields.Many2one(
        comodel_name="account.move", 
        string="Documento"
    )

    # def edit_detexp(self):
    #     ctx = {
    #         'default_nfe40_nDraw': self.name,
    #         'default_nfe40_nRE': self.registro_exp,
    #         'default_nfe40_chNFe': self.chava_nfe,
    #         'default_nfe40_qExport': self.q_export,
    #         'default_company_id': self.company_id.id,
    #         'default_aml_id': self.aml_id.id,
    #         'detexp_id': self.id,
    #         'default_am_id': self.aml_id.move_id.id,
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'wizard.create.detexp',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'context': ctx,
    #     }
 