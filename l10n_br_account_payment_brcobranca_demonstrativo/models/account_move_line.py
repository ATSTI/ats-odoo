# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def send_payment(self):
        res = super().send_payment() 
        for boleto in res:
            for move_line in self.filtered(lambda t: t.document_number == boleto.get("documento_numero")):
                demonstrativo_line = ""
                for line_item in move_line.move_id.invoice_line_ids:
                    demonstrativo_line += line_item.name[line_item.name.find(']')+2:].upper()
                boleto.update(
                    {
                        "demonstrativo": demonstrativo_line + ": " + move_line.date_maturity.strftime("%m-%Y"),
                    }
                )
        return res
