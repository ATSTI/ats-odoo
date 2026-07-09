# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _, fields
from odoo.exceptions import UserError
import re
from datetime import datetime, timedelta
import time
import base64
import tempfile
import requests
from io import BytesIO
import unicodedata
from unidecode import unidecode
from odoo.addons.br_boleto.boleto.document import Boleto


class PaymentOrderLine(models.Model):
    _inherit = 'payment.order.line'

    url = "https://openapi.bradesco.com.br/boleto/cobranca-registro/v1/cobranca"
    url_sandbox = "https://openapisandbox.prebanco.com.br/boleto/cobranca-registro/v1/cobranca"
    url_token = "https://openapi.bradesco.com.br/auth/server-mtls/v2/token"
    url_token_sandbox = "https://openapisandbox.prebanco.com.br/auth/server-mtls/v2/token"

    def remover_acentos(self, texto):
        # Normaliza a string para o formato NFKD (separa o caractere do acento)
        texto_normalizado = unicodedata.normalize('NFKD', texto)
        # Filtra mantendo apenas caracteres que não sejam acentos (marcas)
        return "".join(c for c in texto_normalizado if not unicodedata.combining(c))

    def generate_payment_order_line(self, move_line):
        """Gera um objeto de payment.order ao imprimir um boleto"""
        order_name = self.env['ir.sequence'].next_by_code('payment.order')
        payment_mode = move_line.payment_mode_id
        payment_order = self.env['payment.order'].search([
            ('state', '=', 'draft'),
            ('payment_mode_id', '=', payment_mode.id)], limit=1)
        order_dict = {
            'name': u'%s' % order_name,
            'user_id': self.env.user.id,
            'payment_mode_id': move_line.payment_mode_id.id,
            'state': 'draft',
            'currency_id': move_line.company_currency_id.id,
            'company_id': payment_mode.journal_id.company_id.id,
            'journal_id': payment_mode.journal_id.id,
            'src_bank_account_id': payment_mode.journal_id.bank_account_id.id,
        }
        if not payment_order:
            payment_order = payment_order.create(order_dict)

        move = self.env['payment.order.line'].search(
            [('src_bank_account_id', '=',
              payment_mode.journal_id.bank_account_id.id),
             ('move_line_id', '=', move_line.id),
             ('state', 'not in', ('cancelled', 'rejected'))])
        if not move:
            return self.env['payment.order.line'].create({
                'move_line_id': move_line.id,
                'src_bank_account_id':
                payment_mode.journal_id.bank_account_id.id,
                'journal_id': payment_mode.journal_id.id,
                'payment_order_id': payment_order.id,
                'payment_mode_id': move_line.payment_mode_id.id,
                'date_maturity': move_line.date_maturity,
                'partner_id': move_line.partner_id.id,
                'emission_date': move_line.date,
                'amount_total': move_line.amount_residual,
                'name': "%s/%s" % (move_line.move_id.name, move_line.name),
                'nosso_numero':
                payment_mode.nosso_numero_sequence.next_by_id(),
            })
        return move

    def buscar_token(self, diario):
        if diario:
            cert = base64.b64decode(diario.l10n_br_bradesco_cert)
            key = base64.b64decode(diario.l10n_br_bradesco_key)
            token = diario.l10n_br_bradesco_token
            id_bradesco = diario.l10n_br_bradesco_id
            secret = diario.l10n_br_bradesco_secret
            cert_path = tempfile.mkstemp()[1] + '.crt'
            key_path = tempfile.mkstemp()[1] + '.key'

            arq_temp = open(cert_path, "wb")
            arq_temp.write(cert)
            arq_temp.close()

            arq_temp = open(key_path, "wb")
            arq_temp.write(key)
            arq_temp.close()

            agora = datetime.now()
            tempo_token = diario.write_date
            if (agora - tempo_token).total_seconds() > 3500:
                cert = (cert_path, key_path)
                headers = {
                    'accept': 'application/json',
                    'content-type': 'application/x-www-form-urlencoded',
                }
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': diario.l10n_br_bradesco_id,
                    'client_secret': diario.l10n_br_bradesco_secret,
                    'refresh_token': diario.l10n_br_bradesco_token,
                }
                if diario.tipo_ambiente_boleto == "1":
                    url_connect = self.url_token
                else:
                    url_connect = self.url_token_sandbox
                response = requests.post(url_connect, headers=headers, data=data, cert=cert)
                response.raise_for_status()
                token = response.json().get("access_token")
                diario.write({'l10n_br_bradesco_token': token, 'write_date': agora})
            return cert_path, key_path, token, id_bradesco, secret

    def _vals_homologacao_bradesco(self):
        # =====================================================================
        # OBS .  só aceita os dados exatos que estão na documentacao
        # =====================================================================
        payload = {
            "nuCPFCNPJ": 31759489,
            "filialCPFCNPJ": 1,
            "ctrlCPFCNPJ": 55,
            "idProduto": 9,
            "nuNegociacao": 285600000000222652,
            "nuCliente": "1",
            "dtEmissaoTitulo": "27.05.2025",
            "dtVencimentoTitulo": "27.08.2025",
            "vlNominalTitulo": "500.00",
            "cdEspecieTitulo": 2,
            "cindcdAceitSacdo": "2",
            "percentualJuros": 0,
            "vlJuros": "5.00",
            "qtdeDiasJuros": 1,
            "percentualMulta": "20.00",
            "vlMulta": 0,
            "qtdeDiasMulta": 1,
            "percentualDesconto1": 0,
            "vlDesconto1": "50.00",
            "dataLimiteDesconto1": "29.05.2025",
            "nomePagador": "CLIENTE",
            "logradouroPagador": "AVENIDA COPACABANA",
            "nuLogradouroPagador": "237",
            "cepPagador": 0,
            "complementoCepPagador": 0,
            "bairroPagador": "ALPHAVILLE",
            "municipioPagador": "BARUERI",
            "ufPagador": "SP",
            "cdIndCpfcnpjPagador": 1,
            "nuCpfcnpjPagador": 98765432111,
            "nomeSacadorAvalista": "PARCEIRO",
            "logradouroSacadorAvalista": "AV SAO PAULO",
            "nuLogradouroSacadorAvalista": "4",
            "complementoLogradouroSacadorAvalista": "",
            "cepSacadorAvalista": 0,
            "complementoCepSacadorAvalista": 0,
            "bairroSacadorAvalista": "VILA 237",
            "municipioSacadorAvalista": "OSASCO",
            "ufSacadorAvalista": "SP",
            "cdIndCpfcnpjSacadorAvalista": 1,
            "nuCpfcnpjSacadorAvalista": 12345678999,
            "enderecoSacadorAvalista": "RUA BRA",
            "dddFoneSacadorAvalista": 0,
            "foneSacadorAvalista": 0,
            "listaMsgs": [
                {"mensagem": "$$.*$$"},
                {"mensagem": "$$.*$$"}
            ]
        }
        return payload

    def send_information_to_banco_bradesco(self, moveline):
        if moveline:
            diario = moveline.payment_mode_id.journal_id
            instrucao = diario.l10n_br_boleto_instrucoes or ''
            taxa_mora = 0
            valor_juros = 0
            if diario.l10n_br_valor_juros_mora:
                taxa_mora = int(diario.l10n_br_valor_juros_mora*100)
                valor_juros = self.amount_total * (taxa_mora/100)
            taxa_multa = 0
            valor_multa = 0
            if diario.l10n_br_valor_multa:
                taxa_multa = int(diario.l10n_br_valor_multa*100)
                valor_multa = self.amount_total * (taxa_multa/100)
            partner_id = moveline.partner_id.commercial_partner_id
            cliente = unidecode(partner_id.legal_name or partner_id.name)
            email = partner_id.email or ""
            email = email[:email.find(';')]
            emitente_cnpj_raiz = int(moveline.move_id.company_id.cnpj_cpf[:10].replace('.',''))
            emitente_cnpj_filial = int(moveline.move_id.company_id.cnpj_cpf[11:15])
            emitente_cnpj_dv = int(moveline.move_id.company_id.cnpj_cpf[16:18])
            bank = diario.bank_account_id
            nu_negociacao = bank.bra_number + '0000000' + bank.acc_number.zfill(7)
            tipo_cpfcnpj = 2 if moveline.move_id.partner_id.is_company else 1
            cnpj_cpf = re.sub('[^0-9]', '', moveline.move_id.partner_id.cnpj_cpf or '')

            vals = {
                "nuCPFCNPJ": emitente_cnpj_raiz,
                "filialCPFCNPJ": emitente_cnpj_filial,
                "ctrlCPFCNPJ": emitente_cnpj_dv,
                "idProduto": 9,
                "nuNegociacao": nu_negociacao,
                "nuCliente": str(moveline.l10n_br_order_line_id.identifier),
                "dtEmissaoTitulo": moveline.l10n_br_order_line_id.emission_date.strftime('%d.%m.%Y'),
                "dtVencimentoTitulo": moveline.l10n_br_order_line_id.date_maturity.strftime('%d.%m.%Y'),
                "vlNominalTitulo": "%.02f" % moveline.l10n_br_order_line_id.amount_total,
                "cdEspecieTitulo": 2,
                "cindcdAceitSacdo": "2",
                "percentualJuros": str(taxa_mora),
                "vlJuros": "%.02f" % valor_juros,
                "qtdeDiasJuros": 1,
                "percentualMulta": str(taxa_multa),
                "vlMulta": "%.02f" % valor_multa,
                "qtdeDiasMulta": 1,
                "percentualDesconto1": 0,
                "vlDesconto1": "0",
                "dataLimiteDesconto1": "",
                "nomePagador": cliente,
                "logradouroPagador": self.remover_acentos(moveline.move_id.partner_id.street),
                "nuLogradouroPagador": moveline.move_id.partner_id.number,
                "cepPagador": moveline.move_id.partner_id.zip[:5],
                "complementoCepPagador": moveline.move_id.partner_id.zip[6:9],
                "bairroPagador": self.remover_acentos(moveline.move_id.partner_id.district),
                "municipioPagador": self.remover_acentos(moveline.move_id.partner_id.city_id.name),
                "ufPagador": moveline.move_id.partner_id.state_id.code,
                "cdIndCpfcnpjPagador": tipo_cpfcnpj,
                "nuCpfcnpjPagador": cnpj_cpf,
                "nomeSacadorAvalista": "",
                "logradouroSacadorAvalista": "",
                "nuLogradouroSacadorAvalista": "",
                "complementoLogradouroSacadorAvalista": "",
                "cepSacadorAvalista": 0,
                "complementoCepSacadorAvalista": 0,
                "bairroSacadorAvalista": "",
                "municipioSacadorAvalista": "",
                "ufSacadorAvalista": "",
                "cdIndCpfcnpjSacadorAvalista": 1,
                "nuCpfcnpjSacadorAvalista": 0,
                "enderecoSacadorAvalista": "",
                "dddFoneSacadorAvalista": 0,
                "foneSacadorAvalista": 0,
                "listaMsgs": [
                    {"mensagem": instrucao}
                ]
            }

            cert_path, key_path, token, id_bradesco, secret = self.buscar_token(diario)
            cert = base64.b64decode(diario.l10n_br_bradesco_cert)
            key = base64.b64decode(diario.l10n_br_bradesco_key)
            arq_temp = open(cert_path, "wb")
            arq_temp.write(cert)
            arq_temp.close()

            arq_temp = open(key_path, "wb")
            arq_temp.write(key)
            arq_temp.close()

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer %s" %(token)
            }
            cert = (cert_path, key_path)
            if diario.tipo_ambiente_boleto == "1":
                url_connect = self.url
            else:
                url_connect = self.url_sandbox
                vals = self._vals_homologacao_bradesco()
            response = requests.post(url_connect, json=vals, headers=headers, cert=cert)

            nosso_numero = ''
            if response.status_code == 200:
                json_p = response.json()
                nosso_numero = json_p["nuTituloGerado"]
                linha_digitavel = json_p["linhaDigitavel"]
                codigo_barras = json_p["cdBarras"]
                moveline.write({'nosso_numero': nosso_numero,
                    'codigo_barra': codigo_barras,
                    'linha_digitavel': linha_digitavel,
                    'boleto_emitido': True,})
                move = self.env['payment.order.line'].search(
                    [('src_bank_account_id', '=',
                    diario.bank_account_id.id),
                    ('move_line_id', '=', moveline.id),
                    ('state', 'not in', ('cancelled', 'rejected'))])
                if move:
                    move.write({
                        'state':'processed',
                        'nosso_numero': nosso_numero,
                    })
                return True
            elif response.status_code == 401:
                moveline.write({'codigo_barra': 'Erro autorização consultar API'})
                return False
            else:
                msg_erro = 'Erro:\n%s' %(response.text)
                moveline.invoice_id.message_post(body=_(msg_erro))
                moveline.write({'codigo_barra': 'Houve erro na API'})
                return False

    def baixa_faturas(self, move_line_id, valor, journal_id, juros):
        invoices = move_line_id.invoice_id
        if move_line_id.amount_residual > valor or ((move_line_id.amount_residual - valor) > 0.01):
            baixar_tudo = 'open'
        else:
            baixar_tudo = 'reconcile'
        bank_account = invoices[0].partner_bank_id or self.partner_bank_account_id

        payment_type = 'inbound'# if move_line_id.debit else 'outbound'
        payment_methods = \
            payment_type == 'inbound' and \
            journal_id.inbound_payment_method_ids or \
            journal_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        conta_juros = ''
        juros_desc = ''
        if juros:
            cc = self.env['account.account'].search([
                    ('name', 'ilike', 'Juros Recebidos'),
                    ('company_id', '=', journal_id.company_id.id),
            ])
            conta_juros = cc.id
            juros_desc = 'Juros recebido %s - %s' %(move_line_id.partner_id.name, move_line_id.name or '')

        vals = {
            'journal_id': journal_id.id,
            'payment_method_id': payment_method_id.id,
            'payment_date': datetime.now(),
            'communication': invoices.name,
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': payment_type,
            'amount': valor+juros,
            'currency_id': journal_id.company_id.currency_id.id,
            'partner_id': move_line_id.partner_id.id,
            'partner_type': 'customer',
            'partner_bank_account_id': bank_account.id,
            'multi': False,
            'payment_difference_handling': baixar_tudo,
            'writeoff_account_id': conta_juros,
            'writeoff_label': juros_desc
        }
        Payment = self.env['account.payment']
        pay = Payment.create(vals)
        pay.post()

    def action_register_boleto(self, move_lines):
        not_boleto = False
        gerado = False
        for item in move_lines:
            if item.payment_mode_id.boleto:
                not_boleto = True
            if item.boleto_emitido:
                gerado = True
        if not not_boleto:
            raise UserError(_('Modo de pagamento não é boleto!'))
        if gerado:
            raise UserError(_('Boleto ja emitido!'))
        for line in move_lines:
            if line.nosso_numero:
                continue
            if line.payment_mode_id.boleto:
                order_line = self.generate_payment_order_line(line)
            else:
                continue
            line.write({'l10n_br_order_line_id': order_line.id})
            self |= order_line
            if line.payment_mode_id and line.payment_mode_id.journal_id.l10n_br_use_boleto_bradesco:
                gerado = self.send_information_to_banco_bradesco(line)
                if len(move_lines)>3:
                    time.sleep(3)
                if gerado:
                    line.write({'boleto_emitido': True})
                    boleto_list = order_line.generate_boleto_list()
                    pdf_string = Boleto.get_pdfs(boleto_list)
                    if pdf_string:
                        nome_boleto = 'boleto_%s_%s.pdf' %(
                            line.name, str(line.id)
                        )
                        attachment_obj = self.env['ir.attachment']
                        vls_boleto = {
                            'name': nome_boleto,
                            'datas_fname': nome_boleto,
                            'datas': base64.b64encode(pdf_string),
                            'mimetype': 'application/pdf',
                            'res_model': 'account.invoice',
                            'res_id': line.invoice_id.id,
                        }
                        attachment_obj.sudo().create(vls_boleto)
        return self

    def generate_boleto_list(self):
        if self.filtered(lambda x: x.state in ('cancelled', 'rejected')):
            raise UserError(
                _('Boletos cancelados ou rejeitados não permitem a impressão'))
        return  super(PaymentOrderLine, self).generate_boleto_list()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    codigo_barra = fields.Char(string=u"Codigo Barras", size=48)
    linha_digitavel = fields.Char(string=u"Linha Digitavel", size=48)
