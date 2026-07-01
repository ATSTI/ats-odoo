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
from unidecode import unidecode
#from ..boleto.document import Boleto


class PaymentOrderLine(models.Model):
    _inherit = 'payment.order.line'

    url = "https://openapi.bradesco.com.br/boleto/cobranca-registro/v1/cobranca"
    url_sandbox = "https://openapisandbox.prebanco.com.br/boleto/cobranca-registro/v1/cobranca"
    url_token = "https://openapi.bradesco.com.br/auth/server-mtls/v2/token"
    url_token_sandbox = "https://openapisandbox.prebanco.com.br/auth/server-mtls/v2/token"


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

            arq_temp = open(cert_path, "w")
            arq_temp.write(cert.decode())
            arq_temp.close()

            arq_temp = open(key_path, "w")
            arq_temp.write(key.decode())
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
                    'client_id': "63f3a0f9-2cce-4bd0-81a6-e59c4369f811",
                    'client_secret': "67837173-eee2-424e-bd53-9382d106f698",
                    'refresh_token': "TG-68386dce65f462000124cc8f-2431081876",
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

    # def buscando_boleto_inter(self, moveline, nosso_numero):
    #     url_boleto = self.url + '/cobranca/v2/boletos/%s' %(nosso_numero)

    #     cert_path, key_path, token, id_inter, secret = self.buscar_token(diario)
    #     headers = {
    #         "Authorization": "Bearer " + token
    #     }

    #     response = requests.get(url_boleto, headers=headers, cert=(cert_path, key_path))
    #     if response.status_code != 200:
    #         moveline.write({'codigo_barra': 'Busca Boleto falhou.'})
    #     if response.status_code == 200:
    #         json_p = response.json()
    #         nosso_numero = json_p["nossoNumero"]
    #         linha_digitavel = json_p["linhaDigitavel"]
    #         codigo_barras = json_p["codigoBarras"]
    #         moveline.write({'nosso_numero': nosso_numero,
    #                 'codigo_barra': codigo_barras,
    #                 'linha_digitavel': linha_digitavel,
    #                 'boleto_emitido': True,})
    #         move = self.env['payment.order.line'].search(
    #                 [('src_bank_account_id', '=',
    #         diario.bank_account_id.id),
    #                 ('move_line_id', '=', moveline.id),
    #                 ('state', 'not in', ('cancelled', 'rejected'))])
    #         if move:
    #             move.write({'state':'processed'})

    # def pegar_pdf_inter(self, moveline, nosso_numero):
    #     url_pdf = self.url + '/cobranca/v2/boletos/%s/pdf' %(nosso_numero)

    #     cert_path, key_path, token, id_inter, secret = self.buscar_token(moveline.payment_mode_id.journal_id)

    #     request_body = "client_id=" + id_inter + "&client_secret=" + secret + "&scope=boleto-cobranca.write boleto-cobranca.read extrato.read&grant_type=client_credentials"
    #     headers = {
    #         "Accept": "application/json",
    #         "Content-Type": "application/json",
    #         "Authorization": "Bearer " + token,
    #     }

    #     response = requests.get(url_pdf, headers=headers, cert=(cert_path, key_path), data=request_body)
    #     json_p = response.json()
    #     if response.status_code != 200:
    #         moveline.write({'codigo_barra': 'Busca PDF falhou.'})
    #         #raise ValueError("Não foi possível resgatar as informações do boleto.")
    #     else:
    #         pdf = BytesIO(base64.b64decode(json_p['pdf']))
    #         nome_boleto = 'boleto_%s_%s.pdf' %(moveline.invoice_id.number, str(moveline.name or moveline.id))
    #         arq_temp = open('/tmp/'+nome_boleto, "wb")
    #         arq_temp.write(pdf.read())
    #         arq_temp.close()
    #         arq_temp = open('/tmp/'+nome_boleto, "rb")
    #         pdf = arq_temp.read()
    #         arq_temp.close()
    #         # TODO
    #         # anexar o PDF na FATURA
    #         attachment_obj = self.env['ir.attachment']
    #         attachment_obj.create(dict(
    #             name=nome_boleto,
    #             datas_fname=nome_boleto,
    #             datas=base64.b64encode(pdf),
    #             mimetype='application/pdf',
    #             res_model='account.invoice',
    #             res_id=moveline.invoice_id.id,
    #         ))

    def send_information_to_banco_bradesco(self, moveline):
        if moveline:
            diario = moveline.payment_mode_id.journal_id
            instrucao = diario.l10n_br_boleto_instrucoes or ''
            taxa_mora = 0
            valor_juros = 0
            if diario.l10n_br_valor_juros_mora:
                taxa_mora = diario.l10n_br_valor_juros_mora
                valor_juros = self.amount_total * (taxa_mora/100)
            taxa_multa = 0
            valor_multa = 0
            if diario.l10n_br_valor_multa:
                taxa_multa = diario.l10n_br_valor_multa
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
                "dtEmissaoTitulo": moveline.l10n_br_order_line_id.emission_date.strftime('%d-%m-%Y'),
                "dtVencimentoTitulo": moveline.l10n_br_order_line_id.date_maturity.strftime('%d-%m-%Y'),
                "vlNominalTitulo": str(moveline.l10n_br_order_line_id.amount_total),
                "cdEspecieTitulo": 2,
                "cindcdAceitSacdo": "2",
                "percentualJuros": str(taxa_mora),
                "vlJuros": str(valor_juros),
                "qtdeDiasJuros": 1,
                "percentualMulta": str(taxa_multa),
                "vlMulta": str(valor_multa),
                "qtdeDiasMulta": 1,
                "percentualDesconto1": 0,
                "vlDesconto1": "0",
                "dataLimiteDesconto1": "",
                "nomePagador": cliente,
                "logradouroPagador": moveline.move_id.partner_id.street,
                "nuLogradouroPagador": moveline.move_id.partner_id.number,
                "cepPagador": moveline.move_id.partner_id.zip[:5],
                "complementoCepPagador": moveline.move_id.partner_id.zip[6:9],
                "bairroPagador": moveline.move_id.partner_id.district,
                "municipioPagador": moveline.move_id.partner_id.city_id.name,
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

            # url_cobranca = "https://openapi.bradesco.com.br/boleto/cobranca-registro/v1/cobranca"
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
                    move.write({'state':'processed'})

                # self.pegar_pdf_inter(moveline, nosso_numero)

            elif response.status_code == 401:
                moveline.write({'codigo_barra': 'Erro autorização consultar API'})
            else:
                msg_erro = 'Erro:\n%s' %(response.text)
                moveline.invoice_id.message_post(body=_(msg_erro))
                moveline.write({'codigo_barra': 'Houve erro na API'})
                #raise UserError('Houve um erro com a API do Banco Inter:\n%s' % response.text)

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

    # def search_information_to_banco_inter(self, diario):
    #     # teste pegar PDF
    #     # moveline = self.env['account.move.line'].browse([40787])
    #     # nosso_numero = '00841740287'
    #     # self.pegar_pdf_inter(moveline, nosso_numero)
    #     # # self.buscando_boleto_inter(moveline, nosso_numero)
    #     # return True

    #     diario = self.env['account.journal'].browse([diario])

    #     cert_path, key_path, token, id_inter, secret = self.buscar_token(diario)

    #     headers = {
    #         "Authorization": "Bearer " + token
    #     }
    #     dia = fields.Date.today().day
    #     data_ini = fields.Date.today().strftime('%Y-%m-%d') # '2021-08-01' # fields.Datatime.now()
    #     data_ini = data_ini[:8] + str(dia-5).zfill(2)
    #     data_fim =  fields.Date.today().strftime('%Y-%m-%d') # '2021-09-24' #fields.Datatime.now()

    #     opFiltros = {
    #         'dataInicial': data_ini,
    #         'dataFinal': data_fim,
    #         'situacao': 'PAGO',
    #         'tipoOrdenacao': 'ASC',
    #         'itensPorPagina': 10,
    #         'paginaAtual': 0
    #     }
    #     #    'filtrarDataPor': 'EMISSAO',
    #     #    'nome': '',
    #     #    'email': '',
    #     #    'cpfCnpj': '',
    #     #    'nossoNumero': '',
    #     #    'ordenarPor': 'NOSSONUMERO',

    #     response = requests.get(
    #         self.url + "/cobranca/v2/boletos",
    #         params=opFiltros,
    #         headers=headers,
    #         cert=(cert_path, key_path)
    #     )
    #     if response.status_code == 200:
    #         json_p = response.json()
    #         for boleto in json_p["content"]:
    #             line = self.env['account.move.line'].search([
    #                 ('nosso_numero', '=', boleto['nossoNumero']),
    #             ])
    #             valor = boleto["valorTotalRecebimento"]
    #             valor_nominal = boleto["valorNominal"]
    #             juros = valor - valor_nominal
    #             if not line:
    #                 rotulo = boleto['seuNumero'][-2:]
    #                 fatura = boleto['seuNumero']
    #                 fatura = fatura[:len(fatura)-2]
    #                 invoice = self.env['account.invoice'].search([
    #                    ('number', '=', fatura)
    #                 ])
    #                 if invoice:
    #                     line = self.env['account.move.line'].search([
    #                         ('name', '=', rotulo),
    #                         ('invoice_id', '=', invoice.id),
    #                     ])
    #                 if line and not line.nosso_numero:
    #                     line.write({'nosso_numero': boleto['nossoNumero']})
    #             if not line:
    #                 continue
    #             move = self.env['payment.order.line'].search(
    #                 [('src_bank_account_id', '=',
    #                 diario.bank_account_id.id),
    #                 ('move_line_id', '=', line.id),
    #                 ('state', 'in', ('draft', 'processed'))])
    #             if move:
    #                 if line.invoice_id.state == 'open':
    #                     move.write({'state':'paid'})
    #                     self.baixa_faturas(line, valor, diario, juros)
    #     #elif response.status_code == 401:
    #     #    raise UserError("Erro de autorização ao consultar a API do Banco Inter")
    #     #else:
    #     #    raise UserError('Houve um erro com a API do Banco Inter:\n%s' % response.text)
    #     else:
    #          x = "deu erro" + response.text

    def action_register_boleto(self, move_lines):
        boleto = 'N'
        for item in move_lines:
            if boleto == 'S':
                continue
            if item.payment_mode_id.type != 'receivable':
                boleto = 'N'
            else:
                boleto = 'S'
            if not item.payment_mode_id.boleto:
                boleto = 'N'
            else:
                boleto = 'S'
        if not boleto:
            raise UserError(_('Modo de pagamento não é boleto!'))
        # aqui se for INTER , executo outra coisa
        boleto_inter = 'N'
        for move_line in move_lines:
            if move_line.nosso_numero:
                continue
            #if boleto_inter == 'S':
            #    continue
            if move_line.payment_mode_id.boleto:
                order_line = self.generate_payment_order_line(move_line)
            else:
                continue
            move_line.write({'l10n_br_order_line_id': order_line.id})
            self |= order_line
            if move_line.payment_mode_id and move_line.payment_mode_id.journal_id.l10n_br_use_boleto_bradesco:
                self.send_information_to_banco_bradesco(move_line)
                if len(move_lines)>3:
                    time.sleep(3)
                boleto_inter = 'S'
        if boleto_inter == 'N':
            move_lines.write({'boleto_emitido': True})
        return self

    def generate_boleto_list(self):
        if self.filtered(lambda x: x.state in ('cancelled', 'rejected')):
            raise UserError(
                _('Boletos cancelados ou rejeitados não permitem a impressão'))
        return  super(PaymentOrderLine, self).generate_boleto_list()

    def action_print_boleto(self):
        for item in self:
            if item.payment_mode_id.type != 'receivable':
                raise UserError(_('Modo de pagamento não é boleto!'))
            if not item.payment_mode_id.boleto:
                raise UserError(_('Modo de pagamento não é boleto!'))
        return self.env.ref(
            'br_boleto.action_boleto_payment_order_line').report_action(self)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    codigo_barra = fields.Char(string=u"Codigo Barras", size=48)
    linha_digitavel = fields.Char(string=u"Linha Digitavel", size=48)
