# Copyright 2022 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_bank import sanitize_account_number


_logger = logging.getLogger(__name__)

class AccountStatementImport(models.TransientModel):

    _inherit = "account.statement.import"

    @api.model
    def _prepare_ofx_transaction_line(self, transaction):
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

        if not memo:
            return vals

        partner = self._find_partner_from_memo(memo, float(transaction.amount))
        if partner and len(partner) == 1:
            vals["partner_id"] = partner.id

        return vals


    def _find_partner_from_memo(self, memo, amount):
        """Tenta identificar o parceiro a partir do memo do extrato."""

        # --- PIX ---
        if memo.startswith("Pix"):
            ref = self._extract_memo_ref(memo, prefix_len=28)
            if not ref:
                return False

            partners = self.env["res.partner"].search([
                ("name", "=ilike", ref),   # =ilike: case-insensitive mas exato
                ("parent_id", "=", False),
            ])

            if not partners:
                return False
            if len(partners) == 1:
                return partners

            # Mais de um: desambiguar pela fatura em aberto
            for partner in partners:
                move = self.env["account.move"].search([
                    ("partner_id", "=", partner.id),
                    ("amount_total", "=", amount),
                    ("state", "=", "posted"),
                    ("payment_state", "not in", ["paid", "in_payment"]),
                ], limit=1)
                if move:
                    return partner   # primeiro parceiro com fatura válida

            return False  # ambíguo, não arrisca

        # --- BOLETO ---
        if memo.startswith("Boleto"):
            ref = self._extract_memo_ref(memo, prefix_len=34)
            if not ref:
                return False

            aml = self.env["account.move.line"].search([
                ("own_number", "=", ref),
            ], limit=1)

            return aml.partner_id if aml and len(aml.partner_id) == 1 else False

        return False


    def _extract_memo_ref(self, memo, prefix_len):
        """Extrai a referência do memo com base no offset do banco.
        Loga um warning se o resultado parecer inválido.
        """
        ref = memo[prefix_len:].strip().rstrip(".")  # mais robusto que [:len-1]
        if not ref:
            _logger.warning("OFX: memo '%s' não contém referência no offset %s", memo, prefix_len)
        return ref
