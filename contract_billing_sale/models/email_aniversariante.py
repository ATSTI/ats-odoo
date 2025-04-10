# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from datetime import datetime, timedelta
from dateutil import parser
import time

class EmailAniversariante(models.Model):
    _name = 'email.aniversariante'
    _inherit = ['mail.thread']
    _description = "Relacao de aniversariantes"

    def _send_mail(self, mail_to, email_from=None, context=None):
        """
        Send mail for event invitation to event attendees.
        @param email_from: email address for user sending the mail
        @return: True
        """
        #mail_to = 'sabrina@myplaceoffice.com.br;mario@myplaceoffice.com.br;carlos@atsti.com.br'
        mail_to = 'crsilveira@gmail.com'
        corpo = ''

        if mail_to and email_from and corpo:
            #ics_file = self.get_ics_file(cr, uid, res_obj, context=context)
            vals = {'email_from': email_from,
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': 'Relatorio de Envio de boleto.',
                    'body_html': corpo,
                    'auto_delete': False}
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        return True

    def cron_aniversariante(self, mes_niver=0):
        mes = datetime.now()
        if mes_niver == 0: 
            mes_niver = mes.month
        prt_ids = self.env['res.partner'].search([('customer','=', True)])
        tabela = '<table cellspacing="1" border="1" cellpadding="4" width="70%"><tr>\
            <td>Titular</td>\
            <td>Aniversariante</td>\
            <td>Data</td>\
            <td>Idade</td>\
            </tr>'
        a = ''
        for p in prt_ids:
            if p.data_nascimento:
                m_niver = p.data_nascimento.month
                idade = 0
                if mes_niver == m_niver:
                    idade = mes.year - p.data_nascimento.year
                if idade in (18,25,60,80):
                    if p.parent_id:
                        titular = p.parent_id.name
                    else:
                        titular = ''
                    #import pudb;pu.db
                    dt_niver = '%s-%s-%s' %(
                        str(p.data_nascimento.day).zfill(2),
                        str(p.data_nascimento.month).zfill(2),
                        str(p.data_nascimento.year))
                    a += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %(
                        titular, p.name, dt_niver, idade)
        if a:
            tabela = tabela + a + '</table>'
            mail_to = 'crsilveira@gmail.com'
            assunto = 'Relatório de Aniversariantes: %s-%s' %(
                str(mes.month).zfill(2),
                str(mes.year))
            mail_data = {'email_from': 'ats@atsti.com.br',
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': assunto,
                    'body_html': tabela,
                    'auto_delete': False}
            #import pudb;pu.db
            try:
                domain=[('name','like','Email_Aniversariante')]
                mail = self.env['mail.template'].search(domain, limit=1)
                mail.body_html = tabela
                mail.subject = assunto
                mail.send_mail(self.id)
            except ValueError:
                mail = False
            #x = self.env['mail.mail'].send(mail_data)
