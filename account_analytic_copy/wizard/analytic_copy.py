# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import ValidationError



class AnalyticCopy(models.TransientModel):
    _name = "analytic.copy"
    _description = "Account Analytic"

    account_group = fields.Many2many('account.analytic.group', string='Grupo de Contas')
    partner_id = fields.Many2one('res.partner', string='Cliente')

    def action_copy(self):
        for grupo in self.account_group:
            analytic = self.env['account.analytic.account']
            contas = analytic.search([
                ('group_id', '=', grupo.id),
                ('partner_id', '=', False),
            ])
            for conta in contas:
                ccriadas = analytic.search([
                    ('name', '=', conta.name),
                    ('group_id', '=', conta.group_id.id),
                    ('partner_id', '=', self.partner_id.id),
                ])
                if ccriadas:
                    continue
                analytic.create({
                    'name': conta.name,
                    'code': conta.code,
                    'partner_id': self.partner_id.id,
                    'group_id': conta.group_id.id,
                })
        return True