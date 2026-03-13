from odoo import models, fields, api

class CrmClaimCost(models.Model):
    _name = "crm.claim.cost"
    _description = "Custos da Reclamação"

    claim_id = fields.Many2one("crm.claim", string="Reclamação")

    descricao = fields.Char(string="Descrição")
    valor = fields.Float(string="Valor")
    quantidade = fields.Float(string="Quantidade", default=1)

    total = fields.Float(
        string="Total",
        compute="_compute_total",
        store=True
    )

    @api.depends("valor", "quantidade")
    def _compute_total(self):
        for rec in self:
            rec.total = rec.valor * rec.quantidade