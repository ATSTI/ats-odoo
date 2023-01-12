# Copyright 2020 ForgeFlow S.L. (https://forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    origin = fields.Char(
        string="Origem",
    )    
    
    def action_done(self):
        state = self.env['maintenance.stage'].search([('done', '=', True)])
        self.write({'stage_id': state.id})
        # TODO criar e concluir uma devolucao para o estoque