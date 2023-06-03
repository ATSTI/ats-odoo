# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from datetime import timedelta
import logging
from .arquivo_certificado import ArquivoCertificado

from odoo import api, models, _, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from erpbrasil.bank.inter.boleto import BoletoInter
    from erpbrasil.bank.inter.api import ApiInter
except ImportError:
    _logger.error("Biblioteca erpbrasil.bank.inter não instalada")

try:
    from erpbrasil.base import misc
except ImportError:
    _logger.error("Biblioteca erpbrasil.base não instalada")


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    def _generate_bank_inter_boleto_data(self):
        dados = []
        instrucao = self.payment_mode_id.instructions or ''
        instrucao1 = ''
        if instrucao and len(instrucao) > 80:
            instrucao = instrucao[:80]
            instrucao1 = instrucao[80:]

        precision = self.env["decimal.precision"]
        precision_account = precision.precision_get("Account")
        for line in self.payment_line_ids:
            move_line = line.move_line_id
            # Instrução de Juros
            tipo_mora = "ISENTO"
            data_mora = ''
            valor_juro = 0
            taxa_mora = 0
            if self.payment_mode_id.boleto_interest_perc > 0.0:
                tipo_mora = "TAXAMENSAL"
                data_mora = (move_line.date_maturity + timedelta(days=1)).isoformat()
                taxa_mora = move_line.payment_mode_id.boleto_interest_perc
                valor_juro = round(
                    move_line.debit
                        * ((move_line.payment_mode_id.boleto_interest_perc / 100) / 30),
                        precision_account,
                    )
            # Instrução Multa
            tipo_multa = "NAOTEMMULTA"
            data_multa = ''
            taxa_multa = 0
            valor_multa = 0
            if move_line.payment_mode_id.boleto_fee_perc > 0.0:
                tipo_multa = "PERCENTUAL"  # Percentual
                data_multa = (move_line.date_maturity + timedelta(days=1)).isoformat()
                taxa_multa = move_line.payment_mode_id.boleto_fee_perc
                valor_multa = round(
                    move_line.debit * (move_line.payment_mode_id.boleto_fee_perc / 100),
                    precision_account,
                )
            # Instrução Desconto
            if move_line.boleto_discount_perc > 0.0:
                valor_desconto = round(
                    move_line.debit * (move_line.boleto_discount_perc / 100),
                    precision_account,
                )
            email = move_line.partner_id.email or ""
            email = email[:email.find(';')]
            vals = {
                "seuNumero": move_line.document_number,
                "dataVencimento": move_line.date_maturity.isoformat(),
                "valorNominal": move_line.debit,
                "numDiasAgenda": 60,
                "pagador":{
                    "cpfCnpj": re.sub("[^0-9]", "",move_line.partner_id.cnpj_cpf),
                    "nome": move_line.partner_id.legal_name,
                    "email": email,
                    "telefone":"",
                    "ddd":"",
                    "cep": re.sub("[^0-9]", "", move_line.partner_id.zip),
                    "numero": move_line.partner_id.street_number or "",
                    "complemento": move_line.partner_id.street2 or "",
                    "bairro": move_line.partner_id.district or "",
                    "cidade": move_line.partner_id.city_id.name or "",
                    "uf": move_line.partner_id.state_id.code or "",
                    "endereco": move_line.partner_id.street_name or "",
                    "tipoPessoa": "JURIDICA" if move_line.partner_id.is_company else "FISICA"
                },
                "mensagem": {
                    "linha1": instrucao,
                    "linha2": instrucao1,
                    "linha3": "",
                    "linha4": "",
                    "linha5": "",
                },
                "desconto1":{
                    "codigoDesconto": "NAOTEMDESCONTO",
                    "taxa": 0,
                    "valor": 0,
                    "data": ""
                },
                "desconto2": {
                    "codigoDesconto": "NAOTEMDESCONTO",
                    "taxa": 0,
                    "valor": 0,
                    "data": ""
                },
                "desconto3":{
                    "codigoDesconto": "NAOTEMDESCONTO",
                    "taxa": 0,
                    "valor": 0,
                    "data": ""
                },
                "multa": {
                    "codigoMulta": tipo_multa,
                    "data": data_multa,
                    "taxa": taxa_multa,
                    "valor": valor_multa,
                },
                "mora": {
                    "codigoMora": tipo_mora,
                    "data": data_mora,
                    "taxa": taxa_mora,
                    "valor": valor_juro,
                },
            }
            dados.append(vals)
        return dados

    def _generate_bank_inter_boleto(self):
        nosso_numero = False
        with ArquivoCertificado(self.journal_id, 'w') as (key, cert):
            api_inter = ApiInter(
                cert=(cert, key),
                conta_corrente=(self.company_partner_bank_id.acc_number +
                                self.company_partner_bank_id.acc_number_dig),
                clientId=self.journal_id.bank_inter_id,
                clientSecret=self.journal_id.bank_inter_secret
            )
            data = self._generate_bank_inter_boleto_data()
            for item in data:
                # DESCOMENTAR a LINHA ABAIXO E COMENTAR A PROXIMA
                # result = api_inter.boleto_inclui(item)
                result = {'seuNumero': '0002/01', 'nossoNumero': '01000227264', 'codigoBarras': '07793937700000003500001112052616101000227264', 'linhaDigitavel': '07790001161205261610410002272648393770000000350'}
                if 'nossoNumero' in result:
                    payment_line_id = self.payment_line_ids.filtered(
                        lambda line: line.document_number == item["seuNumero"])
                    payment_line_id.write({
                        'own_number': result["nossoNumero"],
                        'barcode': result["codigoBarras"],
                        'digitable_line': result["linhaDigitavel"]
                    })
                    payment_line_id.move_line_id.write({
                        'own_number': result["nossoNumero"],
                        'cnab_state': 'accepted'
                    })
                    nosso_numero = result["nossoNumero"]
        return nosso_numero

    def _gererate_bank_inter_api(self):
        """ Realiza a conexão com o a API do banco inter"""
        if self.payment_type == 'inbound':
            boleto = self._generate_bank_inter_boleto()
            # if boleto:
            # busca PDF
            return True
        else:
            raise NotImplementedError

    def generate_payment_file(self):
        self.ensure_one()
        try:
            if (self.company_partner_bank_id.bank_id.code_bc == '077' and
                    self.payment_method_id.code == '240'):
                return self._gererate_bank_inter_api()
            else:
                return super().generate_payment_file()
        except Exception as error:
            raise UserError(_(error))
