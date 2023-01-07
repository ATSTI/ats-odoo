# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _, fields
from odoo.exceptions import UserError
import re
from datetime import timedelta
import time
import datetime
import base64
import tempfile
import requests
from io import BytesIO
from unidecode import unidecode
#from ..boleto.document import Boleto


class PaymentOrderLine(models.Model):
    _inherit = 'payment.order.line'

    url = "https://cdpj.partners.bancointer.com.br"

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
            cert = base64.b64decode(diario.l10n_br_inter_cert)
            key = base64.b64decode(diario.l10n_br_inter_key)
            token = diario.l10n_br_inter_token
            id_inter = diario.l10n_br_inter_id
            secret = diario.l10n_br_inter_secret
            cert_path = tempfile.mkstemp()[1] + '.crt'
            key_path = tempfile.mkstemp()[1] + '.key'

            arq_temp = open(cert_path, "w")
            arq_temp.write(cert.decode())
            arq_temp.close()

            arq_temp = open(key_path, "w")
            arq_temp.write(key.decode())
            arq_temp.close()

            agora = datetime.datetime.now()
            tempo_token = diario.write_date
            #    request_body = "client_id=" + id_inter + "&client_secret=" + secret + "&scope=boleto-cobranca.read boleto-cobranca.write extrato.read&grant_type=client_credentials"
            if (agora - tempo_token).total_seconds() > 3500:
                # url = "https://cdpj.partners.bancointer.com.br"
                request_body = "client_id=" + id_inter + "&client_secret=" + secret + "&scope=boleto-cobranca.write boleto-cobranca.read extrato.read&grant_type=client_credentials"
                response = requests.post(self.url + "/oauth/v2/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    cert=(cert_path, key_path),
                    data=request_body,)
                response.raise_for_status()
                token = response.json().get("access_token")
                diario.write({'l10n_br_inter_token': token, 'write_date': agora})

            return cert_path, key_path, token, id_inter, secret

    def buscando_boleto_inter(self, moveline, nosso_numero):
        url_boleto = self.url + '/cobranca/v2/boletos/%s' %(nosso_numero)

        cert_path, key_path, token, id_inter, secret = self.buscar_token(moveline.payment_mode_id.journal_id)
        headers = {
            "Authorization": "Bearer " + token
        }

        response = requests.get(url_boleto, headers=headers, cert=(cert_path, key_path))
        if response.status_code != 200:
            moveline.write({'codigo_barra': 'Busca Boleto falhou.'})
        if response.status_code == 200:
            json_p = response.json()
            nosso_numero = json_p["nossoNumero"]
            linha_digitavel = json_p["linhaDigitavel"]
            codigo_barras = json_p["codigoBarras"]
            moveline.write({'nosso_numero': nosso_numero, 
                    'codigo_barra': codigo_barras, 
                    'linha_digitavel': linha_digitavel,
                    'boleto_emitido': True,})
            move = self.env['payment.order.line'].search(
                    [('src_bank_account_id', '=',
            moveline.payment_mode_id.journal_id.bank_account_id.id),
                    ('move_line_id', '=', moveline.id),
                    ('state', 'not in', ('cancelled', 'rejected'))])
            if move:
                move.write({'state':'processed'})

    def pegar_pdf_inter(self, moveline, nosso_numero):
        url_pdf = self.url + '/cobranca/v2/boletos/%s/pdf' %(nosso_numero)

        cert_path, key_path, token, id_inter, secret = self.buscar_token(moveline.payment_mode_id.journal_id)

        request_body = "client_id=" + id_inter + "&client_secret=" + secret + "&scope=boleto-cobranca.write boleto-cobranca.read extrato.read&grant_type=client_credentials"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }

        response = requests.get(url_pdf, headers=headers, cert=(cert_path, key_path), data=request_body)
        json_p = response.json()
        if response.status_code != 200:
            moveline.write({'codigo_barra': 'Busca PDF falhou.'})
            #raise ValueError("Não foi possível resgatar as informações do boleto.")
        else:
            pdf = BytesIO(base64.b64decode(json_p['pdf']))
            nome_boleto = 'boleto_%s_%s.pdf' %(moveline.invoice_id.number, str(moveline.name or moveline.id))
            arq_temp = open('/tmp/'+nome_boleto, "wb")
            arq_temp.write(pdf.read())
            arq_temp.close()
            arq_temp = open('/tmp/'+nome_boleto, "rb")
            pdf = arq_temp.read()
            arq_temp.close()
            # TODO 
            # anexar o PDF na FATURA 
            attachment_obj = self.env['ir.attachment']
            attachment_obj.create(dict(
                name=nome_boleto,
                datas_fname=nome_boleto,
                datas=base64.b64encode(pdf),
                mimetype='application/pdf',
                res_model='account.invoice',
                res_id=moveline.invoice_id.id,
            ))

    def send_information_to_banco_inter(self, moveline):
        if moveline:
            #url = "https://apis.bancointer.com.br/openbanking/v1/certificado/boletos"
            # url = "https://cdpj.partners.bancointer.com.br"

            instrucao = moveline.payment_mode_id.journal_id.l10n_br_boleto_instrucoes or ''

            tipo_mora = "ISENTO"
            data_mora = ''
            taxa_mora = 0
            if moveline.payment_mode_id.journal_id.l10n_br_valor_juros_mora:
                tipo_mora = "TAXAMENSAL"
                data_mora = (moveline.date_maturity + timedelta(days=1)).isoformat()
                taxa_mora = moveline.payment_mode_id.journal_id.l10n_br_valor_juros_mora
            tipo_multa = "NAOTEMMULTA"
            data_multa = ''
            taxa_multa = 0
            if moveline.payment_mode_id.journal_id.l10n_br_valor_multa:
                tipo_multa = "PERCENTUAL"  # Percentual
                data_multa = (moveline.date_maturity + timedelta(days=1)).isoformat()
                taxa_multa = moveline.payment_mode_id.journal_id.l10n_br_valor_multa
            partner_id = moveline.partner_id.commercial_partner_id
            cliente = unidecode(partner_id.legal_name or partner_id.name)
            email = partner_id.email or ""
            email = email[:email.find(';')]
            vals = {
                "seuNumero": moveline.invoice_id.number + moveline.name,
                "dataVencimento": moveline.date_maturity.isoformat(),
                "valorNominal": moveline.amount_residual,
                "numDiasAgenda": 60,
                "pagador":{
                    "cpfCnpj": re.sub("[^0-9]", "",partner_id.cnpj_cpf),
                    "nome": cliente,
                    "email": email,
                    "telefone":"",
                    "ddd":"",
                    "cep": re.sub("[^0-9]", "", partner_id.zip),
                    "numero": partner_id.number,
                    "complemento": partner_id.street2 or "",
                    "bairro": unidecode(partner_id.district),
                    "cidade": unidecode(partner_id.city_id.name),
                    "uf": partner_id.state_id.code,
                    "endereco": unidecode(partner_id.street),
                    "tipoPessoa": "FISICA" if partner_id.company_type == "person" else "JURIDICA"
                },
                "mensagem": {
                    "linha1": "",
                    "linha2": "",
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
                    "valor": 0,
                },
                "mora": {
                    "codigoMora": tipo_mora,
                    "data": data_mora,
                    "taxa": taxa_mora,
                    "valor": 0,
                },
            }
            cert_path, key_path, token, id_inter, secret = self.buscar_token(moveline.payment_mode_id.journal_id)

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer %s" %(token)
            }

            response = requests.post(
                    self.url + "/cobranca/v2/boletos",
                    headers=headers,
                    json=vals,
                    cert=(cert_path, key_path)
            )

            nosso_numero = ''
            if response.status_code == 200:
                json_p = response.json()
                nosso_numero = json_p["nossoNumero"]
                linha_digitavel = json_p["linhaDigitavel"]
                codigo_barras = json_p["codigoBarras"]
                moveline.write({'nosso_numero': nosso_numero, 
                    'codigo_barra': codigo_barras, 
                    'linha_digitavel': linha_digitavel,
                    'boleto_emitido': True,})
                move = self.env['payment.order.line'].search(
                    [('src_bank_account_id', '=',
                    moveline.payment_mode_id.journal_id.bank_account_id.id),
                    ('move_line_id', '=', moveline.id),
                    ('state', 'not in', ('cancelled', 'rejected'))])
                if move:
                    move.write({'state':'processed'})
            
                self.pegar_pdf_inter(moveline, nosso_numero)

            elif response.status_code == 401:
                moveline.write({'codigo_barra': 'Erro autorização consultar API'})
            else:
                msg_erro = 'Erro:\n%s' %(response.text)
                moveline.invoice_id.message_post(body=_(msg_erro))
                moveline.write({'codigo_barra': 'Houve erro na API'})
                #raise UserError('Houve um erro com a API do Banco Inter:\n%s' % response.text)

    def search_information_to_banco_inter(self, diario):
        # import pudb;pu.db

        # teste pegar PDF
        # moveline = self.env['account.move.line'].browse([40787])
        # nosso_numero = '00841740287'
        # self.pegar_pdf_inter(moveline, nosso_numero)
        # # self.buscando_boleto_inter(moveline, nosso_numero)
        # return True

        diario = self.env['account.journal'].browse([diario])

        cert_path, key_path, token, id_inter, secret = self.buscar_token(diario)

        headers = {
            "Authorization": "Bearer " + token
        }
        dia = fields.Date.today().day
        data_ini = fields.Date.today().strftime('%Y-%m-%d') # '2021-08-01' # fields.Datatime.now()
        data_ini = data_ini[:8] + str(dia-5).zfill(2)
        data_fim =  fields.Date.today().strftime('%Y-%m-%d') # '2021-09-24' #fields.Datatime.now()

        opFiltros = {
            'dataInicial': data_ini,
            'dataFinal': data_fim,
            'situacao': 'EMABERTO',
            'tipoOrdenacao': 'ASC', 
            'itensPorPagina': 10,
            'paginaAtual': 0
        }
        #    'filtrarDataPor': 'EMISSAO',
        #    'nome': '',
        #    'email': '',
        #    'cpfCnpj': '',
        #    'nossoNumero': '', 
        #    'ordenarPor': 'NOSSONUMERO',            
        
        response = requests.get(
            self.url + "/cobranca/v2/boletos",
            params=opFiltros,
            headers=headers,
            cert=(cert_path, key_path)
        )
        if response.status_code == 200:
            json_p = response.json()
            for boleto in json_p["content"]:
                line = self.env['account.move.line'].search([
                    ('nosso_numero', '=', boleto['nossoNumero']),
                ])
                if not line:
                    rotulo = boleto['seuNumero'][-2:]
                    fatura = boleto['seuNumero']
                    fatura = fatura[:len(fatura)-2]
                    invoice = self.env['account.invoice'].search([
                       ('number', '=', fatura)
                    ])
                    if invoice:
                        line = self.env['account.move.line'].search([
                            ('name', '=', rotulo), 
                            ('invoice_id', '=', invoice.id),
                        ])
                    if line and not line.nosso_numero:
                        line.write({'nosso_numero': boleto['nossoNumero']})
                        
                if not line:
                    continue
                move = self.env['payment.order.line'].search(
                    [('src_bank_account_id', '=',
                    diario.bank_account_id.id),
                    ('move_line_id', '=', line.id),
                    ('state', 'in', ('draft', 'processed'))])
                if move:
                    move.write({'state':'paid'})
        #elif response.status_code == 401:
        #    raise UserError("Erro de autorização ao consultar a API do Banco Inter")
        #else:
        #    raise UserError('Houve um erro com a API do Banco Inter:\n%s' % response.text)
        else:
             x = "deu erro" + response.text
            
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
            if move_line.payment_mode_id and move_line.payment_mode_id.journal_id.l10n_br_use_boleto_inter:
                self.send_information_to_banco_inter(move_line)
                if len(move_lines)>3:
                    time.sleep(3)
                boleto_inter = 'S'
            move_line.write({'l10n_br_order_line_id': order_line.id})
            self |= order_line
        if boleto_inter == 'N':
            move_lines.write({'boleto_emitido': True})
        return self

    def generate_boleto_list(self):
        if self.filtered(lambda x: x.state in ('cancelled', 'rejected')):
            raise UserError(
                _('Boletos cancelados ou rejeitados não permitem a impressão'))
        boleto_list = []
        for line in self:
            if line.payment_mode_id and line.payment_mode_id.journal_id.l10n_br_use_boleto_inter:
                return 'INTER'
            #boleto = Boleto.getBoleto(line, line.nosso_numero)
            #self.env['payment.order.line']
        return  super(PaymentOrderLine, self).generate_boleto_list()
        #    boleto_list.append(boleto.boleto)
        #return boleto_list

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
