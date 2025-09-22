# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime, timedelta


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    date_start = fields.Date('Data de Inicio:')
    date_end = fields.Date('Data Final:')
    state_id = fields.Selection([
            ('andamento', 'Andamento'),
            ('concluido', 'Concluido'),
            ('nao_iniciado', 'Não iniciado'),
        ],
        string="Estágio", default="nao_iniciado", readonly="1"
    )

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start and self.date_end:
            if self.date_start < datetime.now().date() and self.date_end > datetime.now().date():
                self.state_id = 'andamento'
            if self.date_start and self.date_start > datetime.now().date():
                self.state_id = 'nao_iniciado'

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_start and self.date_end:
            if self.date_start < datetime.now().date() and self.date_end > datetime.now().date():
                self.state_id = 'andamento'
            if self.date_end < datetime.now().date():
                self.state_id = 'concluido'
            if self.date_start > self.date_end:
                raise UserWarning('A Data Final não pode ser maior que a Data de Inicio')

