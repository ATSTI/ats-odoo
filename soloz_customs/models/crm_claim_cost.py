from odoo import models, fields

class CrmClaimCost(models.Model):
    _name = "crm.claim.cost"
    _description = "Custos da Reclamação"

    claim_id = fields.Many2one("crm.claim", string="Reclamação")

    descricao = fields.Char(string="Descrição")
    valor = fields.Float(string="Valor")
    total = fields.Float(string="Total")