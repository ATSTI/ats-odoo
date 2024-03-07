# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import ValidationError


class FecharCaixa(models.Model):
    _name = "fechar.caixa"
    _description = "Fechamento de caixa"

    data = fields.Date(string="Data")
    cx = fields.Many2one(
        "res.users", string="Cx", index=True
    )
    sessao = fields.Many2one("pos.session", string="Sessão", index=True)
    sangria = fields.Float("Valor Total das sangrias", compute="_compute_valor_sangria", readonly=True)
    num_sangria = fields.Integer("Nº da sangria", default=1)
    response = fields.Many2one(
        "res.users", string="Responsavel", index=True
    )
    valor_falta = fields.Float("Valor falta")
    valor_sobra = fields.Float("Valor sobra")
    udd = fields.Float("Uso Dinheiro Dia")
    motivo = fields.Char("Motivo")
    analise = fields.Many2one(
        "res.users", string="Analise", index=True
    )
    env_banco = fields.Float("Envio banco")
    env_caixa = fields.Float("Envio caixa geral")
    env_troco = fields.Float("Envio troco")
    obs = fields.Char("Observação")
    situation = fields.Selection(
        selection=[
            ("draft", "Rascunho"),
            ("done", "Feito"),
            ("aproved", "Aprovado"),
        ],
        string="Situação",
        default="draft",
    )

    @api.depends('udd', 'env_banco', 'env_caixa', 'env_troco')
    def _compute_valor_sangria(self):
        for record in self:
            record.sangria = record.udd + record.env_banco + record.env_caixa + record.env_troco
