# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
from datetime import date

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_br_bank_api_inter.parser.inter_file_parser import InterFileParser

from .arquivo_certificado import ArquivoCertificado

from odoo.addons.l10n_br_account_payment_order.constants import (
    BR_CODES_PAYMENT_ORDER,
)

_logger = logging.getLogger(__name__)

try:
    from erpbrasil.bank.inter.api import ApiInter
except ImportError:
    _logger.error("Biblioteca erpbrasil.bank.inter não instalada")

BAIXAS = [
    ("acertos", "Acertos"),
    ("pagodiretoaocliente", "Pago direto ao cliente"),
    ("substituicao", "Substituição"),
    ("apedidodocliente", "A pedido do cliente"),
]

ESTADO = [
    ("emaberto", "Em Aberto"),
    ("pago", "Pago"),
    ("expirado", "Expirado"),
    ("vencido", "Vencido"),
    ("baixado", "Baixado"),
    ("cancelado", "Cancelado"),
]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pdf_boleto_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="PDF Boleto",
        ondelete="cascade",
        copy=False,
    )

    write_off_choice = fields.Selection(
        selection=BAIXAS,
        string="Drop Bank Slip Options",
        default="apedidodocliente",
        copy=False,
    )

    bank_inter_state = fields.Selection(
        selection=ESTADO,
        string="State",
        default="emaberto",
        copy=False,
    )

    write_off_by_api = fields.Boolean(
        string="Slip write off by Bank Inter Api",
        default=False,
        readonly=True,
        copy=False,
    )

    codigo_solicitacao = fields.Char(string="Código Solicitação", copy=False,)
    pix_copiaecola = fields.Char(string="Pix cópia e cola", copy=False,)
    pix_txid = fields.Char(string="Pix id", copy=False,)

    def generate_pdf_boleto(self):
        """
        Creates a new attachment with the Boleto PDF
        """
        if self.own_number and self.pdf_boleto_id:
            return
        order_id = self.payment_line_ids[0].order_id
        with ArquivoCertificado(order_id.journal_id, "w") as (key, cert):
            api = ApiInter(
                cert=(cert, key),
                conta_corrente=(
                    order_id.company_partner_bank_id.acc_number
                    + order_id.company_partner_bank_id.acc_number_dig
                ),
                client_id=self.journal_payment_mode_id.bank_client_id,
                client_secret=self.journal_payment_mode_id.bank_secret_id,
                client_environment=self.journal_payment_mode_id.bank_environment,
            )
            if not self.own_number and self.codigo_solicitacao:
                # buscar informacoes do boleto pegar nosso_numero
                resposta = api.consulta_boleto_detalhado(self.codigo_solicitacao)
                if 'cobrancas' in resposta:
                    for cob in resposta['cobrancas']:
                        boleto = cob['boleto']
                        titulo = cob['cobranca']
                        if titulo['seuNumero'] != self.document_number:
                            continue
                        pix = cob['pix']
                        self.payment_line_ids[0].digitable_line = boleto["linhaDigitavel"]
                        self.payment_line_ids[0].barcode = boleto["codigoBarras"]
                        self.pix_copiaecola = pix['pixCopiaECola']
                        self.pix_txid = pix['txid']
                        if 'nossoNumero' in boleto:
                            self.own_number = boleto["nossoNumero"]
                            self.payment_line_ids[0].own_number = boleto["nossoNumero"]

            datas = api.boleto_pdf(self.codigo_solicitacao)
            datas_json = json.loads(datas.decode("utf-8"))
            self.pdf_boleto_id = self.env["ir.attachment"].create(
                {
                    "name": ("Boleto %s" % self.name),
                    "res_model": 'account.move',
                    "res_id": self.move_id.id,
                    "datas": datas_json["pdf"],
                    "mimetype": "application/pdf",
                    "type": "binary",

                }
            )

    def print_pdf_boleto(self):
        """
        Generates and downloads Boletos PDFs
        :return: actions.act_url
        """

        self.generate_pdf_boleto()

        if self.own_number:
            boleto_id = self.pdf_boleto_id
            base_url = self.env["ir.config_parameter"].get_param("web.base.url")
            download_url = "/web/content/%s/%s?download=True" % (
                str(boleto_id.id),
                boleto_id.name,
            )

            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "new",
            }

    def drop_bank_slip_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Motivo da Baixa",
            "res_model": "bank.api.inter.baixa",
            "src_model": "saas.template",
            "view_type": "form",
            "view_mode": "form",
            "view_id": self.env.ref("l10n_br_bank_api_inter.bank_api_inter_baixa").id,
            "target": "new",
        }

    def drop_bank_slip(self):
        try:
            if self.write_off_choice:
                codigo_baixa = self.write_off_choice.upper()
            else:
                codigo_baixa = "APEDIDODOCLIENTE"
            order_id = self.payment_line_ids.order_id
            if self.bank_inter_state != "pago":
                if self.codigo_solicitacao:
                    with ArquivoCertificado(order_id.journal_id, "w") as (key, cert):
                        api = ApiInter(
                            cert=(cert, key),
                            conta_corrente=(
                                order_id.company_partner_bank_id.acc_number
                                + order_id.company_partner_bank_id.acc_number_dig
                            ),
                            client_id=self.journal_payment_mode_id.bank_client_id,
                            client_secret=self.journal_payment_mode_id.bank_secret_id,
                            client_environment=self.journal_payment_mode_id.bank_environment,
                        )
                        resultado = api.boleto_baixa(self.codigo_solicitacao, codigo_baixa)
                        if resultado:
                            self.bank_inter_state = "baixado"
        except Exception as error:
            raise UserError(_(error))

    def search_bank_slip(self):
        try:
            parser = InterFileParser(self.journal_payment_mode_id)
            for order in self.payment_line_ids:
                with ArquivoCertificado(order.order_id.journal_id, "w") as (key, cert):
                    api = ApiInter(
                        cert=(cert, key),
                        conta_corrente=(
                            order.order_id.company_partner_bank_id.acc_number
                            + order.order_id.company_partner_bank_id.acc_number_dig
                        ),
                        client_id=self.journal_payment_mode_id.bank_client_id,
                        client_secret=self.journal_payment_mode_id.bank_secret_id,
                        client_environment=self.journal_payment_mode_id.bank_environment,
                    )
                    if self.own_number:

                        resposta = api.consulta_boleto_detalhado(
                            nosso_numero=self.own_number
                        )

                        parser.parse(resposta)

                        if resposta["situacao"].lower() != self.bank_inter_state:
                            if resposta["situacao"] == "pago":
                                move_id = self.env["account.move"].create(
                                    {
                                        "date": date.today(),
                                        "ref": self.ref,
                                        "journal_id": self.journal_payment_mode_id.id,
                                        "company_id": self.company_id.id,
                                        "line_ids": [
                                            (
                                                0,
                                                0,
                                                {
                                                    "account_id": self.account_id.id,
                                                    "partner_id": self.partner_id.id,
                                                    "debit": self.move_id.line_ids[
                                                        0
                                                    ].credit,
                                                    "credit": self.move_id.line_ids[
                                                        0
                                                    ].debit,
                                                    "date_maturity": self.date_maturity,
                                                },
                                            ),
                                            (
                                                0,
                                                0,
                                                {
                                                    "account_id": self.account_id.id,
                                                    "partner_id": self.company_id.id,
                                                    "debit": self.move_id.line_ids[
                                                        1
                                                    ].credit,
                                                    "credit": self.move_id.line_ids[
                                                        1
                                                    ].debit,
                                                    "date_maturity": self.date_maturity,
                                                },
                                            ),
                                        ],
                                    }
                                )
                                move_id.post()
                                (move_id.line_ids[0] + self).reconcile()

                            if resposta["situacao"] == "cancelado":
                                self.write_off_by_api = True
                                self.write_off_choice = resposta[
                                    "motivoCancelamento"
                                ].lower()

                        self.bank_inter_state = resposta["situacao"].lower()
        except Exception as error:
            raise UserError(_(error))

    def all_search_bank_slip(self):
        try:
            move_line_ids = self.env["account.move.line"].search(
                [("bank_inter_state", "in", ["emaberto", "vencido"])]
            )
            for move_line in move_line_ids:
                move_line.search_bank_slip()
        except Exception as error:
            raise UserError(_(error))

    def _prepare_payment_line_vals(self, payment_order):
        vals = super()._prepare_payment_line_vals(payment_order)
        # PIX pode ser necessário tanto para integragração via CNAB quanto API.
        if self.partner_id.pix_key_ids:
            vals["partner_pix_id"] = self.partner_id.pix_key_ids[0].id
        # Preenchendo apenas nos casos CNAB
        if self.payment_mode_id.payment_method_code in BR_CODES_PAYMENT_ORDER or self.payment_mode_id.payment_method_code == "electronic":
            vals.update(
                {
                    "own_number": self.own_number,
                    "document_number": self.document_number,
                    "company_title_identification": self.company_title_identification,
                    # Codigo de Instrução do Movimento
                    "mov_instruction_code_id": self.mov_instruction_code_id.id,
                    "communication_type": "cnab",
                    # Campos abaixo estão sendo adicionados devido ao problema de
                    # Ordens de Pagto vinculadas devido o ondelete=restrict no
                    # campo move_line_id do account.payment.line
                    # TODO: Aguardando a possibilidade de alteração no
                    #  modulo account_payment_order na v14
                    "ml_maturity_date": self.date_maturity,
                    "move_id": self.move_id.id,
                    "service_type": self._get_default_service_type(),
                    "discount_value": self.currency_id.round(
                        self.amount_currency * (self.boleto_discount_perc / 100)
                    ),
                }
            )

            # Se for uma solicitação de baixa do título é preciso informar o
            # campo debit o codigo original coloca o amount_residual
            if (
                self.mov_instruction_code_id.id
                == self.payment_mode_id.cnab_write_off_code_id.id
            ):
                vals["amount_currency"] = self.credit or self.debit

            if self.env.context.get("rebate_value"):
                vals["rebate_value"] = self.env.context.get("rebate_value")

            if self.env.context.get("discount_value"):
                vals["discount_value"] = self.env.context.get("discount_value")

        return vals
