# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from datetime import datetime
from dateutil.relativedelta import relativedelta

class ReminderCertificateCron(models.Model):
    _name = 'reminder.certificate.cron'
    _inherit = ['mail.thread']
    _description = "Lembrete de vencimento do certificado"

    def cron_lembrete_certificate(self, dia_vcto=0):
        cert_obj = self.env['l10n_br_fiscal.certificate']
        hj = datetime.now()
        dia_vencimento = hj + relativedelta(days=dia_vcto)
        base_domain = [('date_expiration', '<', dia_vencimento)]
        cert_ids = cert_obj.search(base_domain)

        for cert in cert_ids:
            dif_venc = dia_vencimento - cert.date_expiration
            msg = f"Certificado vence em {str(dia_vcto - dif_venc.days)} dias"
            if dif_venc.days == 1:
                self.env.user.notify_info(message=msg)
            if dif_venc.days == 2:
                self.env.user.notify_info(message=msg)
            if dif_venc.days == 3:
                self.env.user.notify_warning(message=msg)
            if dif_venc.days > 4:
                self.env.user.notify_danger(message=msg)
