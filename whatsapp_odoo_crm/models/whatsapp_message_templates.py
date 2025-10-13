from odoo import fields, models
class WhatsappMessageTemplate(models.Model):
    _name = "whatsapp.message.template"
    _description = "WhatsApp Message Template"

    name = fields.Char("Nome do Template", required=True)
    body = fields.Text("Mensagem", required=True)
    active = fields.Boolean("Ativo", default=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        string="Anexos"
    )
