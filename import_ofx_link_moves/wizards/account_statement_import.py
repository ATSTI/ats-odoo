# Copyright 2022 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import re
import unicodedata

from odoo import _, api, models, fields
from odoo.exceptions import UserError

from odoo.addons.base.models.res_bank import sanitize_account_number


class AccountStatementImport(models.TransientModel):

    _inherit = "account.statement.import"

    @api.model
    def _prepare_ofx_transaction_line(self, transaction):
        payment_ref = payment_name = transaction.payee
        payment_name = re.sub(r"\d+", "", payment_name)
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
                prt = self.find_partner(payment_name, float(transaction.amount))
                if prt and len(prt) > 1:
                    prt = self.choose_best_partner(prt, payment_name.split())
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
                        if not move:
                            prt = False
            if memo.find('Boleto') == 0:
                ref = memo[34:]
                ref = ref[:len(ref)-1]
                aml = self.env["account.move.line"].search([
                    ("own_number", "=", ref)
                ])
                prt = aml.partner_id
                if not prt:
                    prt = self.find_partner(payment_name, float(transaction.amount))
                    if len(prt) > 1:
                        prt = self.choose_best_partner(prt, payment_name.split())
            if prt:
                vals["partner_id"] = prt.id
        return vals
    
    def normalize(self, text):
        if not text:
            return ""
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        text = text.upper()
        text = re.sub(r"[^A-Z ]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def choose_best_partner(self, partners, termos):
        termo_principal = termos[0].upper()

        def score(partner):
            name = self.normalize(partner.name)

            # começa exatamente com o termo
            if name.startswith(termo_principal):
                return 100

            # termo aparece mas não no início
            if f" {termo_principal}" in name:
                return 50

            return 0

        partners = sorted(partners, key=score, reverse=True)

        # só aceita se tiver score > 0
        best = partners[0]
        return best if score(best) > 0 else False

    def find_partner(self, payment_name, amount):
        today = fields.Date.context_today(self)
        date_from = today.replace(day=1)
        date_to = fields.Date.end_of(today, 'month')
        Partner = self.env["res.partner"]
        Lines = self.env["account.move.line"]
        termos = self.normalize(payment_name).split()

        prt = Partner.search([("name", "ilike", " ".join(termos))])
        if prt and len(prt) == 1:
            if prt.parent_id and Lines.search([("partner_id", "=", prt.parent_id.id)]):
                return prt.parent_id
            return prt

        partners = Partner.name_search(
            name=" ".join(termos),
            operator="ilike",
            limit=5,
        )
        partners = Partner.browse([p[0] for p in partners])

        if len(partners) > 1:
            for partner in partners:
                pr = partner.parent_id.id if partner.parent_id else partner.id
                lines = self.env["account.move.line"].search([
                    ("partner_id", "=", pr),
                    ("display_type", "=", "payment_term"),
                    ("date_maturity", ">=", date_from),
                    ("date_maturity", "<=", date_to),
                    ("balance", "<=" if amount < 0 else ">=", abs(amount)),
                    ("parent_state", "=", "posted"),
                    ("reconciled", "=", False),
                ])
                moves = lines.mapped("move_id")
                if len(moves) == 1:
                    return pr

        if len(partners) == 1:
            return partners

        name = ""
        for termo in termos:
            if name:
                name += " " + termo
            else:
                name = termo
            domain = [("name", "ilike", name)]
            prt = Partner.search(domain)
            if prt and len(prt) < 4:
                if self.choose_best_partner(prt, termos) and len(prt) > 1:   
                    return self.choose_best_partner(prt, termos)
                if len(prt) == 1:
                    return prt

        return False