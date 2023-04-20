# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from datetime import datetime, timedelta

    
class CertificadoSendEmail(models.Model):
    _name = "certificado.send.email"
    
    def send_email_certificado(self, user_id, date1, date2=None):
        company = self.env['res.company'].search([])
        hoje = fields.Date.context_today(self)+timedelta(days=date1)
        for cp in company:
            if cp.certificate_nfe_id.date_expiration.date() == hoje:
                self.enviar_email(user_id, cp)
            if date2:
                hoje_2 = fields.Date.context_today(self)+timedelta(days=date2)
                if cp.certificate_nfe_id.date_expiration.date() == hoje_2:
                    self.enviar_email(user_id, cp)

    def enviar_email(self, user_id, cp):
        user = self.env['res.users'].browse([user_id])
        context = {}
        context['email_to'] = user.email
        context['user_name'] = user.name
        context['email_from'] = self.env.user.email
        context['date_expire'] = datetime.strftime(cp.certificate_nfe_id.date_expiration, '%d-%m-%Y')
        template = self.env.ref('l10n_br_certificado_send_email.vencimento_certificado_send_email', raise_if_not_found=False)
        if template and self.env.user.email:
            template.with_context(context).send_mail(
                self.env.user.id,
                force_send=True,
                raise_exception=False,
                email_values={'recipient_ids': []},
            )