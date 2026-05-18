# Copyright 2004-2020 Odoo S.A.
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import base64
import tempfile
from datetime import datetime, date
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_bank import sanitize_account_number

logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    import_with_api = fields.Boolean(string="Importar via API do Banco Inter")

    data_ini = fields.Date(string="Data início")
    data_fim = fields.Date(string="Data fim")

    journal_id = fields.Many2one("account.journal", string="Diário", default=lambda self: self.env.context.get("journal_id"))
    
    # Para fazer um CRON para essa função
    # modelo = account.statement.import
    # método = import_extract_ofx
    # parametros = data inicio e data fim (YYYY-MM-DD)


    def import_extract_ofx(self, data_ini=None, data_fim=None):
        if data_ini is None:
            data_ini = self.data_ini 
        if data_fim is None:
            data_fim = self.data_fim

        if data_ini > data_fim:
            raise UserError("Data início deve ser menor que data fim.")
        
        if not self.journal_id.bank_inter_cert or not self.journal_id.bank_inter_key:
            raise UserError("Certificado e chave do banco são obrigatórios para importação.")

        file_data, transacoes = self.generate_extract_file(data_ini, data_fim)
        if not transacoes:
            raise UserError("Nenhuma transação encontrada no período selecionado.")
        ofx = self.generate_extract_file_ofx(file_data, transacoes)

        # converte para base64
        ofx_bytes = ofx.encode("latin-1")
        self.statement_file = base64.b64encode(ofx_bytes)

        # opcional: nome do arquivo
        self.statement_filename = "extrato_inter.ofx"
        if self.statement_file:
            self.import_file_button()

        logger.info("OFX gerado com sucesso")
    
    def generate_extract_file(self, data_ini, data_fim):
        clientID = self.journal_id.bank_client_id
        clientSecret = self.journal_id.bank_secret_id
        client_cert, client_key = self.get_cert_files()
        if self.journal_id.bank_environment == "1": #PRODUÇÃO
            url = "https://cdpj.partners.bancointer.com.br"
        else:
            url = "https://cdpj-sandbox.partners.uatinter.co"
        request_body = f"client_id={clientID}&client_secret={clientSecret}&scope=extrato.read&grant_type=client_credentials"

        response = requests.post(url + "/oauth/v2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        cert=(client_cert, client_key),
        data=request_body)

        response.raise_for_status()

        token=response.json().get("access_token")

        totalpaginas = 1
        transacoes = []
        pagina = 0
        while pagina < totalpaginas:
            opFiltros={"dataInicio": self.format_date(data_ini), "dataFim": self.format_date(data_fim), "pagina": pagina, "tamanhoPagina": 30}
            
            cabecalhos={"Authorization": "Bearer " + token, "x-conta-corrente": self.journal_id.bank_account_id.acctid, "Content-Type": "Application/json"}

            response = requests.get("https://cdpj.partners.bancointer.com.br/banking/v2/extrato/completo",
                params=opFiltros,
                headers=cabecalhos,
                cert=(client_cert, client_key)
            )

            if response.status_code != 200:
                logger.error("Erro ao obter extrato: %s", response.text)
                raise UserError("Erro ao obter extrato: %s" % response.text)
            data = response.json()
            if not transacoes:
                transacoes = data.get("transacoes", [])
                totalpaginas = data.get("totalPaginas", 0)
            else:
                transacoes.extend(data.get("transacoes", []))
            if len(data.get("transacoes", [])) < 30:
                break
            pagina += 1
        return data, transacoes


    
    def generate_extract_file_ofx(self, data, transacoes_ofx):

        hoje = datetime.now().strftime("%Y%m%d")

        ofx = []

        ofx.append("OFXHEADER:100")
        ofx.append("DATA:OFXSGML")
        ofx.append("VERSION:102")
        ofx.append("SECURITY:NONE")
        ofx.append("ENCODING:USASCII")
        ofx.append("CHARSET:1252")
        ofx.append("COMPRESSION:NONE")
        ofx.append("OLDFILEUID:NONE")
        ofx.append("NEWFILEUID:NONE")
        ofx.append("")

        ofx.append("<OFX>")

        ofx.append("<SIGNONMSGSRSV1>")
        ofx.append("<SONRS>")
        ofx.append("<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>")
        ofx.append(f"<DTSERVER>{hoje}</DTSERVER>")
        ofx.append("<LANGUAGE>POR</LANGUAGE>")
        ofx.append("<FI>")
        ofx.append("<ORG>Banco Intermedium S/A</ORG>")
        ofx.append("<FID>077</FID>")
        ofx.append("</FI>")
        ofx.append("</SONRS>")
        ofx.append("</SIGNONMSGSRSV1>")

        ofx.append("<BANKMSGSRSV1>")
        ofx.append("<STMTTRNRS>")
        ofx.append("<TRNUID>1</TRNUID>")
        ofx.append("<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>")
        ofx.append("<STMTRS>")
        ofx.append("<CURDEF>BRL</CURDEF>")

        conta = self.journal_id.bank_account_id.acctid
        agencia = self.journal_id.bank_account_id.bra_number

        ofx.append("<BANKACCTFROM>")
        ofx.append("<BANKID>077</BANKID>")
        ofx.append(f"<BRANCHID>{agencia}</BRANCHID>")
        ofx.append(f"<ACCTID>{conta}</ACCTID>")
        ofx.append("<ACCTTYPE>CHECKING</ACCTTYPE>")
        ofx.append("</BANKACCTFROM>")

        datas = [self.format_date(t["dataTransacao"]) for t in transacoes_ofx]
        ofx.append("<BANKTRANLIST>")
        ofx.append(f"<DTSTART>{min(datas)}</DTSTART>")
        ofx.append(f"<DTEND>{max(datas)}</DTEND>")

        for i, t in enumerate(transacoes_ofx):
            tipo_op = t["tipoOperacao"]
            tipo_trans = t["tipoTransacao"]
            cnpj_cpf = ""

            valor = float(t["valor"])
            if tipo_op == "D":
                valor = -valor

            data = self.format_date(t["dataTransacao"])

            # Mapeamento de tipo
            if tipo_trans == "PIX":
                if tipo_op == "C":
                    cnpj_cpf = t['detalhes'].get("cpfCnpjPagador", "")
                else:
                    cnpj_cpf = t['detalhes'].get("cpfCnpjRecebedor", "")
                trntype = "XFER"
            elif tipo_trans in ["PAGAMENTO", "BOLETO_COBRANCA"]:
                cnpj_cpf = t['detalhes'].get("cpfCnpj", "")
                trntype = "PAYMENT"
            elif tipo_trans == "TARIFA":
                trntype = "FEE"
            else:
                trntype = "OTHER"

            descricao = t.get("descricao", "")
            memo = f"{t.get('titulo','')}: \"{descricao}\" - {cnpj_cpf}"

            fitid = t.get("idTransacao", str(i))

            ofx.append("<STMTTRN>")
            ofx.append(f"<TRNTYPE>{trntype}</TRNTYPE>")
            ofx.append(f"<DTPOSTED>{data}</DTPOSTED>")
            ofx.append(f"<TRNAMT>{valor:.2f}</TRNAMT>")
            ofx.append(f"<FITID>{fitid}</FITID>")
            ofx.append("<CHECKNUM>077</CHECKNUM>")
            ofx.append("<REFNUM>077</REFNUM>")
            ofx.append(f"<MEMO>{memo}</MEMO>")
            ofx.append(f"<NAME>{descricao}</NAME>")
            ofx.append("</STMTTRN>")

        ofx.append("</BANKTRANLIST>")

        # SALDO (opcional, mas bom ter)
        ofx.append("<LEDGERBAL>")
        ofx.append("<BALAMT>0.00</BALAMT>")
        ofx.append(f"<DTASOF>{hoje}</DTASOF>")
        ofx.append("</LEDGERBAL>")

        ofx.append("</STMTRS>")
        ofx.append("</STMTTRNRS>")
        ofx.append("</BANKMSGSRSV1>")
        ofx.append("</OFX>")

        return "\n".join(ofx)

    def format_date(self, date_str):
        if isinstance(date_str, str):
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")
        
        elif isinstance(date_str, date):
            return date_str.strftime("%Y-%m-%d")
        
        else:
            raise ValueError(f"Tipo inválido para data: {type(date_str)}")

    def get_cert_files(self):
        cert_b64 = self.journal_id.bank_inter_cert
        key_b64 = self.journal_id.bank_inter_key

        # decode
        cert_bytes = base64.b64decode(cert_b64)
        key_bytes = base64.b64decode(key_b64)

        # cria arquivos temporários
        cert_file = tempfile.NamedTemporaryFile(delete=False)
        key_file = tempfile.NamedTemporaryFile(delete=False)

        cert_file.write(cert_bytes)
        key_file.write(key_bytes)

        cert_file.close()
        key_file.close()

        return cert_file.name, key_file.name