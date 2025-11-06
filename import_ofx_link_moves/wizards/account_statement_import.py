# Copyright 2022 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_bank import sanitize_account_number


class AccountStatementImport(models.TransientModel):

    _inherit = "account.statement.import"

    @api.model
    def _prepare_ofx_transaction_line(self, transaction):
        import pudb;pu.db
        payment_ref = transaction.payee
        memo = ""
        if transaction.checknum:
            payment_ref += " " + transaction.checknum
        if transaction.memo:
            payment_ref += " : " + transaction.memo
            memo = transaction.memo
        vals = {
            "date": transaction.date,
            "payment_ref": payment_ref,
            "amount": float(transaction.amount),
            "unique_import_id": transaction.id,
        }
        if memo:
            prt = False
            if memo.find('Pix') == 0:
                ref = memo[30:]
                ref = ref[:len(ref)-1]
                prt = self.env["res.partner"].search([
                    ("name", "ilike", ref),
                    ("parent_id", "=", False)
                ])
                if prt and len(prt) > 1:
                    for partner in prt:
                        # procurar qual parceiro tem fatura no valor
                        move = self.env["account.move"].search([
                            ("partner_id", "=", partner.id),
                            ("amount_total", "=", float(transaction.amount)),
                            ("state", "=", "posted"),
                            ("payment_state", "not in", ["paid"]),
                        ])
                        if move and len(move) == 1:
                            prt = partner
            if memo.find('Boleto') == 0:
                ref = memo[34:]
                ref = ref[:len(ref)-1]
                aml = self.env["account.move.line"].search([
                    ("own_number", "=", ref)
                ])
                prt = aml.partner_id
                # if not aml:
                #     # procurar fatura pelo valor
                #         move = self.env["account.move"].search([
                #             ("partner_id", "=", partner.id),
                #             ("amount_total", "=", float(transaction.amount)),
                #             ("state", "=", "posted"),
                #             ("payment_state", "not in", "paid"),
                #         ])
                #         if move and len(move) == 1:
                #             prt = partner
            if prt:
                vals["partner_id"] = prt.id
        return vals
