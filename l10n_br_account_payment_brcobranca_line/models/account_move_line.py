# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import requests
import json

from odoo import _, models
from odoo.exceptions import UserError

from odoo.addons.l10n_br_account_payment_order.constants import (
    BR_CODES_PAYMENT_ORDER,
)
from odoo.addons.l10n_br_account_payment_brcobranca.constants.br_cobranca import TIMEOUT, get_brcobranca_api_url


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_draft(self):
        super().button_draft()
        for record in self:
            for line in record.line_ids:
                if line.payment_mode_id.payment_method_code in BR_CODES_PAYMENT_ORDER:                
                    # Verificar a situação do CNAB para apenas apagar
                    # a linha ou mandar uma solicitação de Baixa
                    line.update_cnab_for_cancel_invoice()
                    file_boleto_ids = self.env["ir.attachment"].search([
                        ("name", "ilike", "boleto_nf"),
                        ("res_model", "=", self._name),
                        ("res_id", "=", self.id),
                    ])                    
                    # file_pdf = self.file_boleto_pdf_id
                    self.file_boleto_pdf_id = False
                    file_boleto_ids.unlink()

    def _get_nosso_numero_line(self, move_line, boletos):
        brcobranca_api_url = get_brcobranca_api_url(self.env)
        brcobranca_service_url = brcobranca_api_url + "/api/boleto/nosso_numero"
        for boleto in boletos:
            if 'bank' in boleto:
                del boleto['bank']
            payload = {
                'bank': 'sicredi',
                'data': json.dumps(boleto)
            }

            res = requests.get(
                brcobranca_service_url,
                params=payload,
                timeout=TIMEOUT,
            )
            nosso_numero = res.json()
            for payment in move_line.payment_line_ids:
                if payment.own_number == str(boleto['nosso_numero']).zfill(5) or payment.own_number == str(boleto['nosso_numero']):
                    payment.write({'own_number': nosso_numero})

    def generate_boleto_pdf_line(self, move_line=False):
        file_pdf = self.file_boleto_pdf_id

        if move_line:
            receivable_ids = move_line
        else:
            receivable_ids = self.mapped("due_line_ids")

        boletos = receivable_ids.send_payment()
        if not boletos:
            raise UserError(
                _(
                    "It is not possible generated boletos\n"
                    "Make sure the Invoice are in Confirm state and "
                    "Payment Mode method are CNAB."
                )
            )

        pdf_string = self._get_brcobranca_boleto(boletos)

        # inv_number = self.get_invoice_fiscal_number().split("/")[-1].zfill(8)
        inv_number = move_line.name.replace("/", "_").replace("-", "_")
        file_name = "boleto_nf-" + inv_number + ".pdf"
        if file_pdf:
            if file_pdf.name == file_name:
                self.file_boleto_pdf_id = False
                file_pdf.unlink()

        self.file_boleto_pdf_id = self.env["ir.attachment"].create(
            {
                "name": file_name,
                "store_fname": file_name,
                "res_model": self._name,
                "res_id": self.id,
                "datas": base64.b64encode(pdf_string),
                "mimetype": "application/pdf",
                "type": "binary",
            }
        )
        # Boletos Sicredi: nosso número não é "montado" na remessa
        # para nao gerar divergência entre a remessa e o boleto,
        # é necessário buscar o nosso número gerado no boleto.
        if move_line.payment_mode_id.cnab_config_id.bank_code_bc == "748":
            self._get_nosso_numero_line(move_line, boletos)

    def load_cnab_info_line(self, move_line):
        # Se não possui Modo de Pagto não há nada a ser feito
        if not move_line.payment_mode_id:
            return
        # Se o Modo de Pagto é de saída (pgto fornecedor) não há nada a ser feito.
        if move_line.payment_mode_id.payment_type == "outbound":
            return
        # Se não gera Ordem de Pagto não há nada a ser feito
        if not move_line.payment_mode_id.payment_order_ok:
            return
        # Podem existir Modo de Pagto q geram Ordens mas não são CNAB
        # por isso nesse caso tbm nada a ser feito
        if move_line.payment_mode_id.payment_method_code not in BR_CODES_PAYMENT_ORDER:
            return
        for index, interval in enumerate(move_line):
            # inv_number = self.get_invoice_fiscal_number().split("/")[-1]
            numero_documento = move_line.name.split("-")[0] #.replace("/", "").replace("-", "")
            cnab_config = interval.payment_mode_id.cnab_config_id
            sequence = cnab_config.own_number_sequence_id.next_by_id()

            interval.own_number = sequence if cnab_config.generate_own_number else "0"
            interval.document_number = numero_documento
            interval.company_title_identification = hex(interval.id).upper()
            instructions = ""
            if self.eval_payment_mode_instructions:
                instructions = self.eval_payment_mode_instructions + "\n"
            if self.instructions:
                instructions += self.instructions + "\n"
            interval.instructions = instructions
            # Codigo de Instrução do Movimento pode variar,
            # mesmo no CNAB 240
            interval.instruction_move_code_id = cnab_config.sending_code_id


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def generate_pdf_boleto_line(self):
        """
        Creates a new attachment with the Boleto PDF
        """
        inv_number = self.name.replace("/", "_").replace("-", "_")
        file_name = "boleto_nf-" + inv_number + ".pdf"
        if self.own_number and self.move_id.file_boleto_pdf_id.name == file_name:
            raise UserError(
                _(
                    "Boleto já gerado para esta linha."
                )
            )
        filtered_invoice_ids = self.filtered(
                lambda s: (
                    s.payment_mode_id and s.payment_mode_id.auto_create_payment_order
                )
            )
        
        if self.payment_line_ids:
            # caso ja incluido e mudou vencimento ou valor
            # precisa excluir e gerar novamente para atualizar o boleto
            for payment_line in self.payment_line_ids:
                if payment_line.order_id.state in ("draft", "open"):
                    payment_line.unlink()
                else:
                    raise UserError(
                        _(
                            "Arquivo CNAB já gerado, não é possível alterar o boleto "
                        )
                    )
        if not self.payment_line_ids:
            if filtered_invoice_ids:            
                # Criação das Linha na Ordem de Pagamento
                applicable_lines = False
                for move in self.move_id:
                    if move.state != "posted":
                        raise UserError(_("A fatura %s não foi 'Confirmada'") % move.name)
                    applicable_lines = move.line_ids.filtered(
                        lambda x: (
                            not x.reconciled
                            and x.payment_mode_id.payment_order_ok
                            and x.account_id.account_type in ("asset_receivable", "liability_payable")
                            and not any(
                                p_state in ("draft", "open", "generated")
                                for p_state in x.payment_line_ids.mapped("state")
                            )
                        )
                    )
                    apoo = self.env["account.payment.order"]
                    payorder = apoo.search(
                        self.move_id.get_account_payment_domain(self.payment_mode_id), limit=1
                    )
                    if not payorder:
                        payorder = apoo.create(
                            self.move_id._prepare_new_payment_order(self.payment_mode_id)
                        )                   
                    if applicable_lines:
                        self.move_id.load_cnab_info_line(filtered_invoice_ids)
                        vals = self._prepare_payment_line_vals(payorder)
                        self.env["account.payment.line"].create(vals)
        self.move_id.generate_boleto_pdf_line(filtered_invoice_ids)
        return {
            'type': 'ir.actions.act_window_close'
        }
