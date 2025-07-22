# Copyright (C) 2020  KMEE - www.kmee.com.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
from datetime import datetime

from erpbrasil.assinatura import certificado as cert
from erpbrasil.edoc.nfe import NFe as edoc_nfe
from erpbrasil.transmissao import TransmissaoSOAP
from requests import Session

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    file_document = fields.Binary(related="invoice_ids.fiscal_document_id.file_report_id.datas", string="Document File", readonly=True, invisible=True)
    
    def action_print_danfe(self):
        if self.invoice_ids and self.invoice_ids.fiscal_document_id:
            report = self.env['ir.action.report']
            return report._render_danfe(self.invoice_ids.fiscal_document_id.id)
        else:
            raise UserError(_("Documento Fiscal não encontrado para esse pedido de venda."))
