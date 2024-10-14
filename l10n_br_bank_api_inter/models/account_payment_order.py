# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta

from odoo import _, models, fields
from odoo.exceptions import UserError

from .arquivo_certificado import ArquivoCertificado

_logger = logging.getLogger(__name__)

try:
    from erpbrasil.bank.inter.api import ApiInter
    from erpbrasil.bank.inter.boleto import BoletoInter
except ImportError:
    _logger.error("Biblioteca erpbrasil.bank.inter não instalada")

try:
    from febraban.cnab240.user import User, UserAddress, UserBank
except ImportError:
    _logger.error("Biblioteca febraban não instalada")

try:
    from erpbrasil.base import misc
except ImportError:
    _logger.error("Biblioteca erpbrasil.base não instalada")


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _generate_bank_inter_boleto_data(self):
        dados = []
        myself = User(
            name=self.company_id.legal_name,
            identifier=misc.punctuation_rm(self.company_id.cnpj_cpf),
            bank=UserBank(
                bankId=self.company_partner_bank_id.bank_id.code_bc,
                bankName=self.company_partner_bank_id.bank_id.name,
                accountNumber=self.company_partner_bank_id.acc_number,
                branchCode=self.company_partner_bank_id.bra_number,
                accountVerifier=self.company_partner_bank_id.acc_number_dig,
            ),
            address=UserAddress(
                streetLine1=self.company_id.street or "",
                streetLine2=self.company_id.street_number or "",
                district=self.company_id.district or "",
                city=self.company_id.city_id.name or "",
                stateCode=self.company_id.state_id.code or "",
                zipCode=misc.punctuation_rm(self.company_id.zip),
            ),
        )
        for line in self.payment_line_ids:
            payer = User(
                name=line.partner_id.legal_name or line.partner_id.name,
                identifier=misc.punctuation_rm(line.partner_id.cnpj_cpf),
                address=UserAddress(
                    streetLine1=line.partner_id.street or "",
                    streetLine2=line.partner_id.street_number or "",
                    district=line.partner_id.district or "",
                    city=line.partner_id.city_id.name or "",
                    stateCode=line.partner_id.state_id.code or "",
                    zipCode=misc.punctuation_rm(line.partner_id.zip),
                ),
            )
            slip = BoletoInter(
                sender=myself,
                amount=line.amount_currency,
                payer=payer,
                issue_date=line.create_date,
                due_date=line.ml_maturity_date,
                identifier=line.document_number,
                instructions=[],
            )
            dados.append(slip)
        return dados

    def _generate_bank_inter_boleto(self):
        with ArquivoCertificado(self.journal_id, "w") as (key, cert):
            token = self.generated_api_token("escrita")
            api = ApiInter(
                cert=(cert, key),
                conta_corrente=(
                    self.company_partner_bank_id.acc_number
                    + self.company_partner_bank_id.acc_number_dig
                ),
                client_id=self.journal_id.bank_client_id,
                client_secret=self.journal_id.bank_secret_id,
                client_environment=self.journal_id.bank_environment,
                token=token,
            )            
            data = self._generate_bank_inter_boleto_data()
            for item in data:
                # print(item._emissao_data())
                resposta = api.boleto_inclui(item._emissao_data())
                # print(resposta)
                payment_line_id = self.payment_line_ids.filtered(
                    lambda line: line.document_number == item._identifier
                )
                if payment_line_id:
                    payment_line_id.digitable_line = resposta["codigoSolicitacao"]
                    payment_line_id.move_line_id.codigo_solicitacao = resposta["codigoSolicitacao"]
        return False, False

    def _gererate_bank_inter_api(self):
        """Realiza a conexão com o a API do banco inter"""
        if self.payment_type == "inbound":
            return self._generate_bank_inter_boleto()
        else:
            raise NotImplementedError

    # não consegui usar
    # 
    # def api_inter(self, token, key, cert, tipo):
    #     token = self.generated_api_token(tipo)
    #     api = ApiInter(
    #         cert=(cert, key),
    #         conta_corrente=(
    #             self.company_partner_bank_id.acc_number
    #             + self.company_partner_bank_id.acc_number_dig
    #         ),
    #         client_id=self.journal_id.bank_client_id,
    #         client_secret=self.journal_id.bank_secret_id,
    #         client_environment=self.journal_id.bank_environment,
    #         token=token,
    #     )
    #     return api

    def generated_api_token(self, tipo):
        if tipo == "escrita":
            token_date = self.journal_id.bank_token_date
            token = self.journal_id.bank_token
            if not token_date or not self.journal_id.bank_token:
                token_date = datetime.strptime('2024-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            token_date = self.journal_id.bank_token_date_read
            token = self.journal_id.bank_token_read
            if not token_date or not self.journal_id.bank_token_read:
                token_date = datetime.strptime('2024-01-01 01:00:00', '%Y-%m-%d %H:%M:%S')
        tempo_token = (datetime.now() - token_date).total_seconds()
        with ArquivoCertificado(self.journal_id, "w") as (key, cert):
            # O tempo de vida de um token gerado é de uma hora
            if tempo_token > 3600:
                api = ApiInter(
                    cert=(cert, key),
                    conta_corrente=(
                        self.company_partner_bank_id.acc_number
                        + self.company_partner_bank_id.acc_number_dig
                    ),
                    client_id=self.journal_id.bank_client_id,
                    client_secret=self.journal_id.bank_secret_id,
                    client_environment=self.journal_id.bank_environment,
                    token=None,
                )
                token = api.get_token(tipo)
                if tipo == "escrita":
                    self.journal_id.bank_token = token
                    self.journal_id.bank_token_date = datetime.now()
                else:
                    self.journal_id.bank_token_read = token
                    self.journal_id.bank_token_date_read = datetime.now()
        return token

    def open2generated(self):
        self.ensure_one()
        try:
            if (
                self.company_partner_bank_id.bank_id
                == self.env.ref("l10n_br_base.res_bank_077")
                and self.payment_method_id.code == "electronic"
            ):
                self._gererate_bank_inter_api()
                self.write({
                    "date_generated": fields.Date.context_today(self),
                    "state": "generated",
                    "generated_user_id": self._uid,
                })
            else:
                return super().open2generated()
        except Exception as error:
            raise UserError(_(error))
