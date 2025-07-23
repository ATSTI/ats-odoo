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

    def action_download_danfe(self):
        for order in self:
            invoice = order.invoice_ids.filtered(
                lambda inv: inv.fiscal_document_id and inv.fiscal_document_id.file_report_id
            )
            if not invoice:
                raise UserError("Nenhuma fatura com DANFE disponível foi encontrada.")

            # Pega o primeiro anexo
            attachment = invoice[0].fiscal_document_id.file_report_id
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
