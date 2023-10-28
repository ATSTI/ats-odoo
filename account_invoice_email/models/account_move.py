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

        # import pudb;pu.db
        # envia errado se data ficar errada
        #if dia_vcto == 0:
        #    dia_vencimento = data_vcto[6:10]+'-'+data_vcto[3:5]+'-'+data_vcto[:2]
        #else:
        dia_vencimento = (datetime.now() + timedelta(dia_vcto)).strftime("%Y-%m-%d")
        #dia_vencimento = '2017-03-06'

        base_domain = [
            ('date_maturity', '=', dia_vencimento), 
            ('move_id.email_send','=',False),
            ('account_id.internal_type', '=', 'receivable'),
			('credit', '=', 0),('move_id.state', '=', 'posted'),
			'|',('move_id.fiscal_operation_id.fiscal_type', 'in', ('sale', 'purchase')),
			('move_id.fiscal_operation_id', '=', False)
        ]
        invoice_line_ids = invoice_obj.search(base_domain)
        try:
            if tipo_email == "VCTO":
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
                    atts_ids.append(atts.id)
                mail.attachment_ids = [(6, 0, atts_ids)]
                mail.send_mail(inv.move_id.id)
                inv.move_id.message_post(body=_('Email enviado'))
                inv.move_id.email_send = True
            else:
                # if inv.move_id.payment_mode_id.boleto_type:
                #     inv.move_id.message_post(body=_('Sem boleto anexo na Fatura, Email não enviado.'))
                mail.send_mail(inv.move_id.id)
                inv.move_id.message_post(body=_('Email enviado'))
                inv.move_id.email_send = True
        return True
