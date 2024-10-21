# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import base64
import tempfile
import time
import xlrd
import re
import os.path
from erpbrasil.base.fiscal import cnpj_cpf, ie


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_copiar_fatura(self):
        import pudb;pu.db
        vals = {}
        vals["partner_id"] = self.partner_id
        document = self.env['l10n_br_fiscal.document.type'].search([
            ("code", "=", 55)
        ],limit=1)
        # vals["document_type_id"] = document
        operacao = self.env['l10n_br_fiscal.operation'].search([
            ("name", "ilike", "venda")
        ],limit=1)
        # vals["fiscal_operation_id"] = operacao
        vals["payment_mode_id"] = self.payment_mode_id
        vals["invoice_date_due"] = self.invoice_date_due
        vals["journal_id"] = 25
        vals["document_date"] = self.document_date
        vals["invoice_user_id"] = self.invoice_user_id
        vals["tag_campo"] = self.tag_campo
        # vals["fiscal_document_id"] = self.fiscal_document_id
        move = self.env['account.move'].create(vals)
        move.document_type_id = document.id
        move._onchange_document_type_id()
        move.write({"fiscal_operation_id": operacao, "ind_final": '1', "document_serie_id": 1})
        move._onchange_fiscal_operation_id()
        move.fiscal_document_id = self.fiscal_document_id
        move.fiscal_document_id.document_type_id = document.id
        move.fiscal_document_id._onchange_document_type_id()
        lines = []
        for line in self.invoice_line_ids:
            item = {}
            item["product_id"] = line.product_id.id
            item["quantity"] = line.quantity
            item["product_uom_id"] = line.product_uom_id.id
            item["price_unit"] = line.price_unit
            item["price_subtotal"] = line.price_subtotal
            move.write({'invoice_line_ids': [(0, 0, item)]})
        return move


