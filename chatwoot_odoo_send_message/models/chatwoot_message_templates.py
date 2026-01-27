from odoo import fields, models
class ChatwootMessageTemplate(models.Model):
    _name = "chatwoot.message.template"
    _description = "Chatwoot Message Template"

    name = fields.Char("Nome do Template", required=True)
    body = fields.Text("Mensagem", required=True)
    active = fields.Boolean("Ativo", default=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        string="Anexos"
    )
