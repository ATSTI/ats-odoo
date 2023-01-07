# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from datetime import datetime, timedelta
from dateutil import parser
import time
from odoo import SUPERUSER_ID

class EmailNiver(models.Model):
    _name = 'email.niver'
    _inherit = ['mail.thread']
    _description = "Enviar Email Aniversario"

    @api.model
    def mail_reminder(self):
        today = datetime.now()
        partners = self.env['res.partner'].search([])
        partner_ids = []
        for i in partners:
            if i.birthdate_date:
                #daymonth = datetime.strptime(i.birthdate_date, "%Y-%m-%d")
                daymonth = i.birthdate_date
                if today.day == daymonth.day and today.month == daymonth.month:
                    #self.send_birthday_wish(i.id)
                    partner_ids.append(i.id)
        return partner_ids

    @api.model
    def send_birthday_wish(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        template_id = self.env['ir.model.data'].get_object_reference('email_niver',
                                                                     'email_niver_template')[1]
        template_browse = self.env['mail.template'].browse(template_id)
        partners = self.mail_reminder()
        # emails para os clientes
        for emp_id in partners:
            prt = self.env['res.partner'].browse(emp_id)
            if not prt.email:
                continue
            email_to = prt.email
            corpo = '<br />'
            if prt.parent_id:
                corpo += '<p>%s Bom dia,</p>' %(prt.parent_id.name.split(None, 1)[0])
            else:
                corpo += '<p>%s Bom dia,</p>' %(prt.name.split(None, 1)[0])
            corpo += '<p>Tudo bem por ai ?? </p>'
            corpo += '<br />'
            corpo += '<br />'
            if prt.parent_id:
                if prt.sexo and prt.sexo == 'F':
                    corpo += '<p>Parabéns pelo aniversário da %s comemorado hoje.</p>' %(\
                        prt.name.split(None, 1)[0])
                else:
                    corpo += '<p>Parabéns pelo aniversário do %s comemorado hoje.</p>' %(\
                        prt.name.split(None, 1)[0])
            else:
                corpo += '<p>Parabéns pelo seu aniversário.</p>'
                corpo += '<br />'
            corpo += '<p>Muita Paz e Saúde, para voce e toda sua família.</p>'
            corpo += '<br />'
            corpo += '<br />'
            corpo += '<p>Um forte Abraço</p>'
            corpo += '<br />'
            corpo += '<p>Atenciosamente,</p>'
            corpo += '<br />'
            corpo += '<br />'
            corpo += '<p>Soma Corretora de Seguros</p>'
            corpo += ''
            corpo += ''
            if template_browse:
                values = template_browse.generate_email(emp_id, fields=None)
                values['email_to'] = email_to
                values['email_from'] = su_id.email
                values['res_id'] = False
                values['body_html'] = corpo
                if not values['email_to'] and not values['email_from']:
                    pass
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id)
        # emails para o administrador
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        template_id = self.env['ir.model.data'].get_object_reference('email_niver',
                                                                     'email_lista_aniversariantes')[1]
        template_browse = self.env['mail.template'].browse(template_id)
        tabela = '<table border="1" width="100%">\
                      <tr><th>Aniversariante</th>\
                      <th>Aniversario</th>\
                      <th>Responsavel</th>\
                      <th>Telefone</th>\
                      <th>Situacao</th></tr>'
        lista = ''
        for emp_id in partners:
            prt_id = self.env['res.partner'].browse(emp_id)
            #niver = datetime.strptime(prt_id.birthdate_date, "%Y-%m-%d")
            niver = prt_id.birthdate_date
            niver = '%s-%s-%s' %(str(niver.day).zfill(2),str(niver.month).zfill(2),str(niver.year))
            parent = ''
            fone = ''
            if prt_id.parent_id:
                parent = prt_id.parent_id.name
                if prt_id.parent_id.phone:
                    fone = prt_id.parent_id.phone
                if prt_id.parent_id.mobile:
                    if fone != '':
                        fone += ' - ' + prt_id.parent_id.mobile
                    else:
                        fone = prt_id.parent_id.mobile
            else:
                if prt_id.phone:
                    fone = prt_id.phone
                if prt_id.mobile:
                    if fone != '':
                        fone += ' - ' + prt_id.mobile
                    else:
                        fone = prt_id.mobile
            situacao = '** Sem Email **'
            if prt_id.email:
                situacao = 'Enviado'
            lista += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %(
               prt_id.name, niver, parent, fone,situacao)
            email_to = 'crsilveira@gmail.com'
        if lista != '':
            lista = tabela + lista + '</table>'
            lista = 'Lista dos Aniversariantes de hoje:<br />' + lista
            if template_browse:
                values = template_browse.generate_email(emp_id, fields=None)
                values['email_to'] = 'marcio@somaseguros.com.br'
                values['email_from'] = su_id.email
                values['res_id'] = False
                values['body_html'] = lista
                if not values['email_to'] and not values['email_from']:
                    pass
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id)                
    """
    def aniversariantes(self):
        current_date = datetime.now()
        c_mnth = int(current_date.strftime('%m'))
        c_dt = int(current_date.strftime('%d'))
        lista_ids = self.env['res.partner'].search([('id','=',1)])
        return lista_ids

    def _send_mail(self, ids, mail_to, email_from=None, context=None):
        #mail_to = 'sabrina@myplaceoffice.com.br;mario@myplaceoffice.com.br;carlos@atsti.com.br'
        mail_to = 'crsilveira@gmail.com'
        corpo = ''
        if 'nao_enviada' in context:
            fat_ids = context.get('nao_enviada')
            corpo = 'Faturas com boletos nao enviado:"<br>"'
            num = 1
            for ftn in fat_ids:
                corpo = corpo + str(num) + ' - ' + ftn + ' - ERRO"<br>"'
                num += 1

        if 'enviada' in context:
            fat_ids = context.get('enviada')
            corpo = corpo + 'Faturas com boletos Enviados: "<br>"'
            num = 1
            for ftn in fat_ids:
                corpo = corpo + str(num) + ' - ' + ftn + ' - ENVIADO"<br"'
                num += 1

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

    def cron_send_einvoice(self, dia_vcto=5):
        remind = {}
        invoice_obj = self.env['account.invoice']
        # envia errado se data ficar errada
        #if dia_vcto == 0:
        #    dia_vencimento = data_vcto[6:10]+'-'+data_vcto[3:5]+'-'+data_vcto[:2]
        #else:
        dia_vencimento = (datetime.now() + timedelta(dia_vcto)).strftime("%Y-%m-%d")
        #dia_vencimento = '2017-03-06'
        base_domain = [
            ('date_due', '=', dia_vencimento), 
            ('state','=','open'),
            ('email_send','=',False)
        ]
        invoice_ids = invoice_obj.search(base_domain)
        fatura = {}
        try:
            domain=[('name','like','Email_Envio_Boleto')]
            mail = self.env['mail.template'].search(domain, limit=1)
        except ValueError:
            mail = False

        for inv in invoice_ids:
            if not inv.partner_id.active:
                continue
            attachment_ids = self.env['ir.attachment'].search([('res_model','=','account.invoice'),
                ('res_id','=', inv.id )])
            atts_ids = []
            if attachment_ids:
                for atts in attachment_ids:
                    atts_ids.append(atts.id)
                mail.attachment_ids = [(6, 0, atts_ids)]
                fatura_status = {'enviada':'SIM',
                                 'fatura': inv.move_id.name,
                                 'cliente': inv.partner_id.name,
                                 'ocorrencia': ''
                                }
                mail.send_mail(inv.id)
                inv.message_post(body=_('Email enviado'))
                inv.email_send = True
            else:
                if inv.payment_mode_id.boleto_type:
                    inv.message_post(body=_('Sem boleto anexo na Fatura, Email não enviado.'))
                fatura_status = {'enviada':'NAO',
                                 'fatura': inv.move_id.name,
                                 'cliente': inv.partner_id.name,
                                 'ocorrencia': 'Sem Boleto anexo a Fatura.'
                                }
                #self.message_post(cr, uid, [new_id], body=_("Quotation created"), context=ctx)

                fatura_numero = fatura.setdefault(inv.id,fatura_status)
                #fatura_st = fatura_numero.setdefault('NAOENVIADA', {})
                continue
            fatura_numero = fatura.setdefault(inv.id,fatura_status)
            #fatura_st = fatura_numero.setdefault('ENVIADA', {})
            invoice_id = inv.id
            #self.ensure_one()

            #template_id =self.env['ir.model.data'].get_object_reference('contract_billing','email_einvoice_template')[1]
            #          self.env['mail.template'].browse(template_id).send_mail(attendee.id, force_send=force_send)
            #mail_id = self.env['mail.template'].browse(template_id).send_mail(invoice_id, force_send=False)
            #the_mailmess = mail_pool.browse(mail_id).mail_message_id
            #mailmess_pool.write([the_mailmess.id], vals)
            #mail_ids.append(mail_id)
            #if mail_ids:
            #    res = mail_pool.send(mail_ids)
            #    if not res:



        #template_id =self.env['ir.model.data'].get_object_reference('contract_billing','email_erro_fatura')[1]
        #for data in fatura.items():
        #context["data"] = fatura.items()
        #self.env['email.template'].send_mail(template_id, invoice_id, force_send=True)

        return True

    #def cron_lembrete_einvoice(self, dias_vencimento=13):
    def cron_lembrete_einvoice(self, dia_vcto=0):
        remind = {}
        invoice_obj = self.env['account.invoice']
        #    dia_vencimento = data_vcto[6:10]+'-'+data_vcto[3:5]+'-'+data_vcto[:2]
        #elif dia_vcto == 0 and data_vcto == '01-01-2001':
        # nao pode ser por data pois vai enviar vcto errado se estiver data
        dia_vencimento = (datetime.now() + timedelta(dia_vcto)).strftime("%Y-%m-%d")
        base_domain = [('date_due', '=', dia_vencimento), ('state','=','open')]
        invoice_ids = invoice_obj.search(base_domain)
        try:
            domain=[('name','like','Email_Lembrete_Boleto')]
            mail = self.env['mail.template'].search(domain, limit=1)
        except ValueError:
            mail = False

        for inv in invoice_ids:
            attachment_ids = self.env['ir.attachment'].search([('res_model','=','account.invoice'),
                ('res_id','=', inv.id )])
            atts_ids = []
            if attachment_ids:
                for atts in attachment_ids:
                    atts_ids.append(atts.id)
                mail.attachment_ids = [(6, 0, atts_ids)]
                mail.send_mail(inv.id)
                #inv.message_post(body=_(mail.name))
                #inseri aqui a modificação
                inv.email_send = True

        return True
    """
