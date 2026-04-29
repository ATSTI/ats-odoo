from odoo import fields, api, models
class CondoResidencePets(models.Model):
    _name = "condo.residence.pets"
    _description = "Pets"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade"
    )
    
    name =fields.Text("Descrição")
    raça = fields.Char("Raça")
    nome = fields.Char("Nome do PET")