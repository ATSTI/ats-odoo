# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from collections import defaultdict


class AccountMove(models.Model):

    _inherit = "account.move"

    fatura_duplicata = fields.Boolean('Duplicata da Fatura?')


    @api.onchange("invoice_line_ids")
    def onchange_invoice_line_ids(self):
        import pudb;pu.db
        for line in self.invoice_line_ids:
            if line.cfop_id.finance_move == True:
                self.write({"fatura_duplicata": True})
            else:
                self.fatura_duplicata = False

# class AccountMoveLine(models.Model):

#     _inherit = "account.move.line"

#     @api.onchange("cfop_id")
#     def fatura_dupli(self):
#         import pudb;pu.db
#         if self.cfop_id.finance_move == True:
#             self.move_id.write({"fatura_duplicata": True})
#         else:
#             self.move_id.fatura_duplicata = False