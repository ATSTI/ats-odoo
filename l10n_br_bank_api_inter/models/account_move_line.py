# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, date

from .arquivo_certificado import ArquivoCertificado
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.l10n_br_bank_api_inter.parser.inter_file_parser import InterFileParser

_logger = logging.getLogger(__name__)

try:
    from erpbrasil.bank.inter.boleto import BoletoInter
    from erpbrasil.bank.inter.api import ApiInter
except ImportError:
    _logger.error("Biblioteca erpbrasil.bank.inter não instalada")

BAIXAS = [
    ('acertos', 'Acertos'),
    ('protestado', 'Protestado'),
    ('devolucao', 'Devolução'),
    ('protestoaposbaixa', 'Protesto após baixa'),
    ('pagodiretoaocliente', 'Pago direto ao cliente'),
    ('substituicao', 'Substituição'),
    ('faltadesolucao', 'Falta de solução'),
    ('apedidodocliente', 'A pedido do cliente'),
]

ESTADO = [
    ('emaberto', 'Em Aberto'),
    ('pago', 'Pago'),
    ('expirado', 'Expirado'),
    ('vencido', 'Vencido'),
    ('baixado', 'Baixado'),
]


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    pdf_boleto_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='PDF Boleto',
        ondelete='cascade'
    )

    write_off_choice = fields.Selection(
        selection=BAIXAS,
        string='Drop Bank Slip Options',
        default='apedidodocliente',
    )

    bank_inter_state = fields.Selection(
        selection=ESTADO,
        string="State",
        # readonly=True,
        default="emaberto",
    )

    write_off_by_api = fields.Boolean(
        string='Slip write off by Bank Inter Api',
        default=False,
        readonly=True,
    )

    def send_payment(self):
        # super(AccountMoveLine, self).send_payment()
        wrapped_boleto_list = []
        for move_line in self:
            bank_account_id = move_line.payment_mode_id.fixed_journal_id.bank_account_id
            bank_name_brcobranca = get_brcobranca_bank(
                bank_account_id, move_line.payment_mode_id.payment_method_code
            )
            precision = self.env["decimal.precision"]
            precision_account = precision.precision_get("Account")

            boleto_cnab_api_data = {
                "bank": bank_name_brcobranca[0],
                "valor": str("%.2f" % move_line.debit),
                "cedente": move_line.company_id.partner_id.legal_name,
                "cedente_endereco": (move_line.company_id.partner_id.street_name or "")
                + " "
                + (move_line.company_id.partner_id.street_number or "")
                + ", "
                + (move_line.company_id.partner_id.district or "")
                + ", "
                + (move_line.company_id.partner_id.city_id.name or "")
                + " - "
                + (move_line.company_id.partner_id.state_id.code or "")
                + " "
                + ("CEP:" + move_line.company_id.partner_id.zip or ""),
                "documento_cedente": move_line.company_id.cnpj_cpf,
                "sacado": move_line.partner_id.legal_name,
                "sacado_documento": move_line.partner_id.cnpj_cpf,
                "agencia": bank_account_id.bra_number,
                "conta_corrente": bank_account_id.acc_number,
                "convenio": move_line.payment_mode_id.code_convetion,
                "carteira": str(move_line.payment_mode_id.boleto_wallet),
                "nosso_numero": int(
                    "".join(i for i in move_line.own_number if i.isdigit())
                ),
                "documento_numero": move_line.document_number,
                "data_vencimento": move_line.date_maturity.strftime("%Y/%m/%d"),
                "data_documento": move_line.move_id.invoice_date.strftime("%Y/%m/%d"),
                "especie": move_line.payment_mode_id.boleto_species,
                "moeda": DICT_BRCOBRANCA_CURRENCY["R$"],
                "aceite": move_line.payment_mode_id.boleto_accept,
                "sacado_endereco": (move_line.partner_id.street_name or "")
                + " "
                + (move_line.partner_id.street_number or "")
                + ", "
                + (move_line.partner_id.district or "")
                + ", "
                + (move_line.partner_id.city_id.name or "")
                + " - "
                + (move_line.partner_id.state_id.code or "")
                + " "
                + ("CEP:" + move_line.partner_id.zip or ""),
                "data_processamento": move_line.move_id.invoice_date.strftime(
                    "%Y/%m/%d"
                ),
                "instrucao1": move_line.payment_mode_id.instructions or "",
            }

            # Instrução de Juros
            if move_line.payment_mode_id.boleto_interest_perc > 0.0:
                valor_juros = round(
                    move_line.debit
                    * ((move_line.payment_mode_id.boleto_interest_perc / 100) / 30),
                    precision_account,
                )
                instrucao_juros = (
                    "APÓS VENCIMENTO COBRAR PERCENTUAL"
                    + " DE %s %% AO MÊS ( R$ %s AO DIA )"
                    % (
                        (
                            "%.2f" % move_line.payment_mode_id.boleto_interest_perc
                        ).replace(".", ","),
                        ("%.2f" % valor_juros).replace(".", ","),
                    )
                )
                boleto_cnab_api_data.update(
                    {
                        "instrucao3": instrucao_juros,
                    }
                )

            # Instrução Multa
            if move_line.payment_mode_id.boleto_fee_perc > 0.0:
                valor_multa = round(
                    move_line.debit * (move_line.payment_mode_id.boleto_fee_perc / 100),
                    precision_account,
                )
                instrucao_multa = (
                    "APÓS VENCIMENTO COBRAR MULTA"
                    + " DE %s %% ( R$ %s )"
                    % (
                        ("%.2f" % move_line.payment_mode_id.boleto_fee_perc).replace(
                            ".", ","
                        ),
                        ("%.2f" % valor_multa).replace(".", ","),
                    )
                )
                boleto_cnab_api_data.update(
                    {
                        "instrucao4": instrucao_multa,
                    }
                )

            # Instrução Desconto
            if move_line.boleto_discount_perc > 0.0:
                valor_desconto = round(
                    move_line.debit * (move_line.boleto_discount_perc / 100),
                    precision_account,
                )
                instrucao_desconto_vencimento = (
                    "CONCEDER DESCONTO DE" + " %s %% "
                    "ATÉ O VENCIMENTO EM %s ( R$ %s )"
                    % (
                        ("%.2f" % move_line.boleto_discount_perc).replace(".", ","),
                        move_line.date_maturity.strftime("%d/%m/%Y"),
                        ("%.2f" % valor_desconto).replace(".", ","),
                    )
                )
                boleto_cnab_api_data.update(
                    {
                        "instrucao5": instrucao_desconto_vencimento,
                    }
                )

            bank_account = move_line.payment_mode_id.fixed_journal_id.bank_account_id
            if bank_account_id.bank_id.code_bc in ("021", "004"):
                boleto_cnab_api_data.update(
                    {
                        "digito_conta_corrente": bank_account.acc_number_dig,
                    }
                )

            # Fields used in Sicredi and Sicoob Banks
            if bank_account_id.bank_id.code_bc in ("748", "756"):
                boleto_cnab_api_data.update(
                    {
                        "byte_idt": move_line.payment_mode_id.boleto_byte_idt,
                        "posto": move_line.payment_mode_id.boleto_post,
                    }
                )
            # Campo usado no Unicred
            if bank_account_id.bank_id.code_bc == "136":
                boleto_cnab_api_data.update(
                    {
                        "conta_corrente_dv": bank_account.acc_number_dig,
                    }
                )

            wrapped_boleto_list.append(boleto_cnab_api_data)

        return wrapped_boleto_list

    def generate_pdf_boleto(self):
        """
        Creates a new attachment with the Boleto PDF
        """
        if self.own_number and self.pdf_boleto_id:
            return
        order_id = self.payment_line_ids[0].order_id

        # criar o boleto aqui
        order_id.generate_payment_file()

        with ArquivoCertificado(order_id.journal_id, 'w') as (key, cert):
            partner_bank_id = self.journal_id.bank_account_id
            api_inter = ApiInter(
                cert=(cert, key),
                conta_corrente=(
                        order_id.company_partner_bank_id.acc_number +
                        order_id.company_partner_bank_id.acc_number_dig
                ),
                clientId=self.journal_id.bank_inter_id,
                clientSecret=self.journal_id.bank_inter_secret
            )
            datas = api_inter.boleto_pdf(self.own_number)
            self.pdf_boleto_id = self.env['ir.attachment'].create(
                {
                    'name': (
                            "Boleto %s" % self.bank_payment_line_id.display_name),
                    'datas': datas,
                    'datas_fname': ("boleto_%s.pdf" %
                                    self.bank_payment_line_id.display_name),
                    'type': 'binary'
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
            base_url = self.env['ir.config_parameter'].get_param(
                'web.base.url')
            download_url = '/web/content/%s/%s?download=True' % (
                str(boleto_id.id), boleto_id.name)

            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
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
                if self.own_number:
                    with ArquivoCertificado(order_id.journal_id, 'w') as (key, cert):
                        self.api = ApiInter(
                            cert=(cert, key),
                            conta_corrente=(
                                    order_id.company_partner_bank_id.acc_number +
                                    order_id.company_partner_bank_id.acc_number_dig
                            ),
                            clientId=order_id.journal_id.bank_inter_id,
                            clientSecret=order_id.journal_id.bank_inter_secret
                        )
                        self.api.boleto_baixa(self.own_number, codigo_baixa)
                self.bank_inter_state = "baixado"
        except Exception as error:
            raise UserError(_(error))

    def search_bank_slip(self):
        try:
            parser = InterFileParser(self.journal_payment_mode_id)
            for order in self.payment_line_ids:
                with ArquivoCertificado(order.order_id.journal_id, 'w') as (key, cert):
                    api_inter = ApiInter(
                        cert=(cert, key),
                        conta_corrente=(
                                order.order_id.company_partner_bank_id.acc_number +
                                order.order_id.company_partner_bank_id.acc_number_dig
                        ),
                        clientId=order.order_id.journal_id.bank_inter_id,
                        clientSecret=order.order_id.journal_id.bank_inter_secret
                    )
                    resposta = api_inter.boleto_consulta(nosso_numero=self.own_number)

                    parser.parse(resposta)

                    if resposta['situacao'].lower() != self.bank_inter_state:
                        if resposta['situacao'] == 'pago':
                            move_id = self.env['account.move'].create({
                                'date': date.today(),
                                'ref': self.ref,
                                'journal_id': self.journal_payment_mode_id.id,
                                'company_id': self.company_id.id,
                                'line_ids': [(0, 0, {
                                    'account_id': self.account_id.id,
                                    'partner_id': self.partner_id.id,
                                    'debit': self.move_id.line_ids[0].credit,
                                    'credit': self.move_id.line_ids[0].debit,
                                    'date_maturity': self.date_maturity,
                                }),
                                             (0, 0, {
                                    'account_id': self.account_id.id,
                                    'partner_id': self.company_id.id,
                                    'debit': self.move_id.line_ids[1].credit,
                                    'credit': self.move_id.line_ids[1].debit,
                                    'date_maturity': self.date_maturity,
                                })]
                            })
                            move_id.post()
                            (move_id.line_ids[0] + self).reconcile()

                        if resposta['situacao'] == 'baixado':
                            self.write_off_by_api = True

                    self.bank_inter_state = resposta['situacao'].lower()
        except Exception as error:
            raise UserError(_(error))

    def all_search_bank_slip(self):
        try:
            move_line_ids = self.env["account.move.line"].search([
                ("bank_inter_state", "in", ["emaberto", "vencido"])
            ])
            for move_line in move_line_ids:
                move_line.search_bank_slip()
        except Exception as error:
            raise UserError(_(error))
