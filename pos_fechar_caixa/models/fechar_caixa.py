# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import UserError


class FecharCaixa(models.Model):
    _name = "fechar.caixa"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Fechamento de caixa"

    READONLY_STATES = {
        'done': [('readonly', True)],
        'aproved': [('readonly', True)],
    }
    data = fields.Date(string="Data lançamento", states=READONLY_STATES, default=fields.Date.today)
    cx = fields.Many2one(
        "res.users", string="Caixa", index=True, states=READONLY_STATES, track_visibility='onchange'
    )
    sessao = fields.Many2one(
        "pos.session", 
        string="Sessão", 
        index=True, 
        states=READONLY_STATES, 
        domain="[('user_id', '=', cx)]"
    )
    sangria = fields.Float("Valor total das sangrias", compute="_compute_valor_sangria", readonly=True, states=READONLY_STATES)
    num_sangria = fields.Integer("Nº da sangria", default=1, states=READONLY_STATES)
    response = fields.Many2one(
        "res.users", string="Responsavel", index=True, states=READONLY_STATES, track_visibility='onchange'
    )
    valor_falta = fields.Float("Valor falta", states=READONLY_STATES)
    valor_sobra = fields.Float("Valor sobra", states=READONLY_STATES)
    udd = fields.Float("Uso dinheiro no dia", states=READONLY_STATES)
    motivo = fields.Char("Motivo", states=READONLY_STATES)
    analise = fields.Many2one(
        "res.users", string="Analise", index=True, states=READONLY_STATES, track_visibility='onchange'
    )
    env_banco = fields.Float("Envio banco", states=READONLY_STATES)
    env_caixa = fields.Float("Envio caixa geral", states=READONLY_STATES)
    env_troco = fields.Float("Envio troco", states=READONLY_STATES)
    obs = fields.Char("Observação", states=READONLY_STATES)
    state = fields.Selection(
        selection=[
            ("draft", "Rascunho"),
            ("done", "Feito"),
            ("aproved", "Aprovado"),
        ],
        string="Situação",
        default="draft",
        track_visibility='onchange',
        readonly=True
    )
    saldo_final = fields.Float("Saldo final", states=READONLY_STATES )

    @api.onchange('sessao')
    def onchange_sessao(self):
        for record in self:
            if record.sessao.state == 'opened':
                record.saldo_final = record.sessao.cash_register_total_entry_encoding
            if record.sessao.state == 'closed':
                record.saldo_final = record.sessao.cash_real_transaction

    @api.depends('udd', 'env_banco', 'env_caixa', 'env_troco')
    def _compute_valor_sangria(self):
        for record in self:
            record.sangria = record.udd + record.env_banco + record.env_caixa + record.env_troco
    
    def action_return_draft(self):
        return self.write({'state': 'draft'})

    def action_return_done(self):
        return self.write({'state': 'done'})

    def action_return_aproved(self):
        if self.env.user != self.analise:
            raise UserError(_('Usuario não autorizado a aprovar este lançamento.'))
        return self.write({'state': 'aproved'})
    
    # @api.returns('mail.message', lambda value: value.id)
    # def message_post(self, **kwargs):
    #     if self.env.context.get('mark_rfq_as_sent'):
    #         self.filtered(lambda o: o.state == 'draft').write({'state': 'sent'})
    #     return super(FecharCaixa, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
