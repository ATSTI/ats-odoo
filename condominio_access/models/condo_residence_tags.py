from odoo import fields, api, models
class CondoResidenceTags(models.Model):
    _name = "condo.residence.tags"
    _description = "Tags"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade"
    )
    
    name =fields.Text("Descrição")
    numero_tag = fields.Char("Número da TAG")