# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from datetime import datetime
from dateutil.relativedelta import relativedelta

class Certificate(models.Model):
    _inherit = ['l10n_br_fiscal.certificate']

    def cron_lembrete_certificate(self, dia_vcto=0, intervalo=5, tipo='AMBOS'):
        # tipo = MENSAGEM, EMAIL, AMBOS
        cert_obj = self.env['l10n_br_fiscal.certificate']
        hj = datetime.now()
        dia_vencimento = hj + relativedelta(days=dia_vcto)
        base_domain = [('date_expiration', '>', dia_vencimento)]
        cert_ids = cert_obj.search(base_domain)
        usuarios = self.env['res.users'].search([])
        if tipo in ('AMBOS', 'EMAIL'):
            domain=[('name','like','Aviso certificado')]
            mail = self.env['mail.template'].search(domain, limit=1)
            body = "<table style='border: solid 1px #DDD;border-collapse: collapse;padding: 2px 3px;text-align: center;'><caption>Certificados vencendo</caption>"
            body += "<tr><th style='border: solid 1px #DDD;border-collapse: collapse;padding: 2px 3px;text-align: center;'>Empresa</th><th style='border: solid 1px #DDD;border-collapse: collapse;padding: 2px 3px;text-align: center;'>Vence em(dias)</th><th style='border: solid 1px #DDD;border-collapse: collapse;padding: 2px 3px;text-align: center;'>Vencimento</th></tr>"
            body_cert = ""
            body_save = mail.body_html
            for cert in cert_ids:
                dif_venc = dia_vencimento - cert.date_expiration
                if dif_venc.days > (intervalo*6):
                    continue
                body_cert += f"<tr><td style='border: solid 1px #DDD;border-collapse: collapse;padding: 2px 3px;text-align: center;'>{cert.owner_name}</td><td style='border: solid 1px #DDD;border-collapse: collapse;padding: 2px 3px;text-align: center;'>{dif_venc.days}</td><td style='border: solid 1px #DDD;border-collapse: collapse;padding: 2px 3px;text-align: center;'>{cert.date_expiration}</td></tr>"
            if body_cert:
                body_cert += "</table><br>"
                mail.body_html = mail.body_html.replace('msg_certificate', body + body_cert)
                mail.send_mail(cert.id)
                mail.body_html = body_save
                # inv.move_id.message_post(body=_('Email enviado'))
        if tipo in ('AMBOS', 'MENSAGEM'):
            for cert in cert_ids:
                dif_venc = dia_vencimento - cert.date_expiration
                if dif_venc.days > (intervalo*6):
                    continue
                msg = f"Certificado {cert.name}, vence em {str(dia_vcto - dif_venc.days)} dias"
                for user in usuarios:
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

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        data = res.date_expiration - relativedelta(days=15)
        todos = {
            'res_id': res.id,
            'res_model_id': self.env['ir.model'].search([('model', '=', 'l10n_br_fiscal.certificate')]).id,
            'user_id': self.env.uid,
            'activity_type_id': 1,
            'date_deadline': data,
        }
        self.env['mail.activity'].create(todos)
        return res
