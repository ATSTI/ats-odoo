# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    # @api.model
    # def create(self, vals):
    #     if "code" not in vals:
    #         vals["code"] = self._default_code()
    #     return super().create(vals)

    # @api.model
    # def _default_code(self):
    #     return self.env["ir.sequence"].next_by_code("account.analytic.account.code")

    # @api.model
    # def _assign_default_codes(self):
    #     for aaa in self.with_context(active_test=False).search([("code", "=", False)]):
    #         aaa.code = self._default_code()

    @api.onchange('date_start')
    def _onchange_date_start(self):
        # import wdb
        # wdb.set_trace()
        if self.date_start:
            self.write({'state_id': 'andamento'})

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end and self.state_id == 'andamento':
            self.state_id = 'concluido'

    #     @api.onchange('date_end')
    # def _onchange_date_end(self):
    #     if not self.date_end or self.date_end > self.date_start:
    #         self.state_id = 'andamento'