from odoo import models,fields,api

class CrmClaim(models.Model):
    _inherit = "crm.claim"

    cost_ids = fields.One2many(
        "crm.claim.cost",
        "claim_id",
        string="Custos"
    )



