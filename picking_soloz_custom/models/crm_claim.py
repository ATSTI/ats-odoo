from odoo import models,fields,api

class CrmClaim(models.Model):
    _inherit = "crm.claim"

    cost_ids = fields.One2many(
        "crm.claim.cost",
        "claim_id",
        string="Custos"
    )

    total_cost = fields.Float(
        string="Total Geral",
        compute="_compute_total_cost",
        store=True
    )

    @api.depends("cost_ids.total")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.cost_ids.mapped("total"))