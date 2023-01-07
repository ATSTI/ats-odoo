# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from datetime import datetime, timedelta
from dateutil import parser
import time

class EmailEinvoice(models.Model):
    _name = 'email.einvoice'
    _inherit = ['mail.thread']
    _description = "Enviar Cobranca Email"

    def _send_mail(self, ids, mail_to, email_from=None, context=None):
        """
        Send mail for event invitation to event attendees.
        @param email_from: email address for user sending the mail
        @return: True
        """
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
                """
                self.message_post(cr, uid, [inv.id], body=_("Esta fatura : %s nao foi enviado Boleto." %(inv.move_id.name)) ,
                              subtype='Nao enviado boleto nesta fatura Texto',
                              subject='Nao enviado boleto nesta fatura',
                              type="notification",
                              partner_ids=[(1, 3)],
                              context=context)
                context['fatura_naoenviada'] = 'Fatura - %s nao enviada, sem boleto anexo.' %(inv.move_id.name)
                """
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
            """
                    #self.message_post(cr, uid, [inv.id], body='Erro para enviar Boleto: %s ' %(inv.move_id.name) ,
                    #                          subtype='Erro no envio de boleto',
                    #                          subject='Erro no envio do boleto - %s' %(inv.move_id.name),
                    #                          type="notification",
                    #                          partner_ids=[(1, 3)],
                    #                          context=context)
                    #context['fatura_naoenviada'] = 'Fatura %s nao enviada.' %(inv.move_id.name)
                    template_id =self.env['ir.model.data'].get_object_reference('contract_billing','email_erro_fatura')[1]
                    self.env['mail.template'].send_mail(template_id, invoice_id, force_send=True)
                else:
                    txt_comment = 'Enviado Boleto'
                    if inv.comment:
                        txt_comment = inv.comment + ' Enviado Boleto'
                    invoice_altera['comment'] = txt_comment
                    invoice_obj.write([invoice_id], invoice_altera)
            """




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
