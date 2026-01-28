import requests
from odoo import models, fields
from datetime import timedelta

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    chatwoot_id = fields.Many2one(
        'chatwoot.instance', 
        string="Instância",
        domain=[('account_id', '=', "1")],
    )

    def action_notify_activity_cron(self):
        MailActivity = self.env['mail.activity']
        self.chatwoot_id = chatwoot_id = self.env['chatwoot.instance'].search([("account_id", "=", "1")], limit=1)
        vencimento = fields.Date.today() + timedelta(days=chatwoot_id.activity_due_days)
        activities = MailActivity.search([('date_deadline', '=', vencimento)])
        status = "resolved"
        team_id = 36 #ATS INTERNO
        for activity in activities:
            notify = f"""
            Olá {activity.user_id.name},
            Você tem uma atividade pendente:
                Tipo: {activity.activity_type_id.name}
                Assunto: {activity.summary}
                Nota: {activity.note}
            Vencimento: {activity.date_deadline}
            """
            phone_number = f"{activity.user_id.partner_id.phone_sanitized}"
            conversation_id = chatwoot_id.create_new_conversation(phone_number, activity.user_id.partner_id, status, team_id, notify)
            if conversation_id:
                conversation_id = conversation_id.get('id')
            # chatwoot_id.send_text(conversation_id, notify)
            # chatwoot_id.set_resolved_conversation(conversation_id)

class ChatwootInstance(models.Model):
    _inherit = 'chatwoot.instance'

    activity_due_days = fields.Integer(
        string="Dias para notificação de atividades",
        default=1,
        help="Número de dias antes do vencimento da atividade para enviar a notificação.",
    )


        