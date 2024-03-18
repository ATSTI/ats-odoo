# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tests import Form
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    email_send = fields.Boolean(string="Email enviado")

    def cron_email_fatura_cobranca(self, dia_vcto=5, tipo_email="VCTO"):
        
        invoice_obj = self.env['account.move.line']

        dia_vencimento = (datetime.now() + timedelta(dia_vcto)).strftime("%Y-%m-%d")

        base_domain = [
            ('move_id.email_send','=',False),
            ('account_id.internal_type', '=', 'receivable'),
   	        ('credit', '=', 0),('move_id.state', '=', 'posted'),
			'|',('move_id.fiscal_operation_id.fiscal_type', 'in', ('sale', 'purchase')),
			('move_id.fiscal_operation_id', '=', False)
        ]
        if tipo_email != 'CRIADA':
            base_domain.append(('date_maturity', '=', dia_vencimento))
        else:
            newdatetime = (datetime.now() + timedelta(dia_vcto)).replace(hour=1, minute=1)
            base_domain.append(('create_date', '>', newdatetime))
        invoice_line_ids = invoice_obj.search(base_domain)
        try:
            if tipo_email in ('VCTO', 'CRIADA'):
                domain=[('name','like','Fatura: Cobranca')]
            else:
                domain=[('name','like','Fatura: aviso vencimento')]
            mail = self.env['mail.template'].search(domain, limit=1)
        except ValueError:
            mail = False

        for inv in invoice_line_ids:
            attachment_ids = self.env['ir.attachment'].search([('res_model','=','account.move'),
                ('res_id','=', inv.move_id.id )])
            atts_ids = []
            if attachment_ids:
                for atts in attachment_ids:
                    #attachment = {
                    #   'name': ("%s" %atts.filename),
                    #   'datas': atts.get_file_data(),
                    #   'datas_fname': atts.filename,
                    #   'res_model': 'account.move.line',
                    #   'type': 'binary'
                    #}
                    anexo = atts.copy()
                    #atts_ids.append(atts.id)
                mail.attachment_ids =  False
                #mail.attachment_ids = [(0, 0, anexo.id)]
                mail.attachment_ids =  [(4, anexo.id)]    
                mail.send_mail(inv.id)
                inv.move_id.message_post(body=_('Email enviado'))
                inv.move_id.email_send = True
            else:
                # if inv.move_id.payment_mode_id.boleto_type:
                #     inv.move_id.message_post(body=_('Sem boleto anexo na Fatura, Email não enviado.'))
                mail.attachment_ids =  False
                mail.send_mail(inv.id)
                inv.move_id.message_post(body=_('Email enviado'))
                inv.move_id.email_send = True
        return True
