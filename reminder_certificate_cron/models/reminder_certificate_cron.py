# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from datetime import datetime
from dateutil.relativedelta import relativedelta

class ReminderCertificateCron(models.Model):
    _name = 'reminder.certificate.cron'
    _inherit = ['mail.thread']
    _description = "Lembrete de vencimento do certificado"

    def cron_lembrete_certificate(self, dia_vcto=0, intervalo=5):
        cert_obj = self.env['l10n_br_fiscal.certificate']
        hj = datetime.now()
        dia_vencimento = hj + relativedelta(days=dia_vcto)
        base_domain = [('date_expiration', '<', dia_vencimento)]
        cert_ids = cert_obj.search(base_domain)
        usuarios = self.env['res.users'].search([])
        for cert in cert_ids:
            dif_venc = dia_vencimento - cert.date_expiration
            if dif_venc.days > 30:
                continue
            msg = f"Certificado {cert.name}, vence em {str(dia_vcto - dif_venc.days)} dias"
            for user in usuarios:
                # x.notify_info(message=msg)
                if dif_venc.days > (intervalo*5):
                    user.notify_info(message=msg)
                elif dif_venc.days > (intervalo*3):
                    user.notify_info(message=msg)
                elif dif_venc.days > (intervalo*2):
                    user.notify_warning(message=msg)
                elif dif_venc.days > intervalo:
                    user.notify_danger(message=msg)
                else:
                    user.notify_danger(message=msg)


