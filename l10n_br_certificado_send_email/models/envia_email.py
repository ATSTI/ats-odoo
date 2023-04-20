# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from datetime import datetime, timedelta

    
class CertificadoSendEmail(models.Model):
    _name = "send.email"
    
    def send_email_certificado(self, user_id):
        hoje = fields.Date.context_today(self)+timedelta(days=+10)
        company = self.env['res.company'].search([()])
        context['email_to'] = 'crsilveira@gmail.com'
        context['user_name'] = user_id.name
        context['email_from'] = user_id.email_from
        for cp in company:
            if cp.cert_expire_date == hoje:
                context['date_expire'] = cp.cert_expire_date
                mail_template = self.env['mail.template'].search([('name', '=', 'vencimento_certificado')])
                mail_tempĺate.send_mail(cp.id, context=context)
