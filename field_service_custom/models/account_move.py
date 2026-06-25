# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import base64
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        journal_id = self.env.context.get('default_journal_id')

        if journal_id:
            res['journal_id'] = journal_id

        return res
    
    @api.onchange('partner_id')
    def _onchange_partner_keep_journal(self):
        journal_id = self.env.context.get('default_journal_id')

        if journal_id:
            self.journal_id = journal_id



    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        self.narration = 'Data de Coleta: .......... / /2025 - 00:00\nData de Retirada: ....... / /2025 - 00:00'
        return res
  
    def get_payment_date(self):
        self.ensure_one()
        for rec in self.line_ids:
            if rec.full_reconcile_id:
                # pega a primeira linha conciliada com data
                for reconciled_line in rec.full_reconcile_id.reconciled_line_ids:
                    if reconciled_line.date:
                        return reconciled_line.date.strftime('%d/%m/%y') 
    
    def action_open_product_print_wizard(self): #metodo para imprimir o cupom dos produtos q ele quiser na fatura
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Selecionar Produtos",
            "res_model": "account.move.product.print",
            "view_mode": "form",
            "target": "new",
            "context": {"default_move_id": self.id},
        }

# tentei isto aqui pois eu vi no metodo account.move que existe o campo date_maturity, porem nao exibiu nada
    # def get_payment_date(self):
    #     self.ensure_one() #uma fatura por vez apenas
    #     for line in self.line_ids:
    #         if hasattr(line, 'payment_id') and line.payment_id:
    #             return line.payment_id.date_maturity
        
    #     return False

    def attach_account_fullist(self, move=None):
        #Anexando faturamento total
        report = self.env.ref('field_service_custom.report_account_document_id')
        pdf_content, _ = report._render_qweb_pdf([move.id])

        self.env['ir.attachment'].create({
            'name': f'faturamento_total.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': move._name,
            'res_id': move.id,
            'mimetype': 'application/pdf',
        })

    def action_group_products_lines(self):
        for move in self:
            move.attach_account_fullist(move)

            line_to_create = False
            lines_to_remove = self.env["account.move.line"]

            for line in move.invoice_line_ids:
                same_lines = move.invoice_line_ids.filtered(
                    lambda l:
                        l.product_id == line.product_id
                        and l.price_unit == line.price_unit
                )

                if len(same_lines) <= 1:
                    continue

                first_line = same_lines[0]

                line_to_create = {
                    "product_id": first_line.product_id.id,
                    "name": first_line.name,
                    "product_uom_id": first_line.product_uom_id.id,
                    "quantity": sum(same_lines.mapped("quantity")),
                    "price_unit": first_line.price_unit,
                    "account_id": first_line.account_id.id,
                    "tax_ids": [(6, 0, first_line.tax_ids.ids)],
                }

                lines_to_remove = same_lines
                break

            if not line_to_create:
                continue

            move.write({
                "invoice_line_ids": [
                    (0, 0, line_to_create),
                    *[(2, line.id) for line in lines_to_remove],
                ]
            })

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    date_line = fields.Date(string='Data da Linha', help='Data da linha de fatura', default=datetime.now())