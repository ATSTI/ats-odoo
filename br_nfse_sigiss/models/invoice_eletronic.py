# © 2021 Carlos R. Silveira <ats@atsti.com.br, ATS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import pytz
import time
import base64
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
from datetime import timedelta
import json
import requests
import xml.etree.ElementTree as ET
from io import BytesIO

_logger = logging.getLogger(__name__)

try:
    from pytrustnfe.nfse.ginfes import xml_recepcionar_lote_rps
    from pytrustnfe.nfse.ginfes import recepcionar_lote_rps
    from pytrustnfe.nfse.ginfes import consultar_situacao_lote
    from pytrustnfe.nfse.ginfes import consultar_lote_rps
    from pytrustnfe.nfse.ginfes import cancelar_nfse
    from pytrustnfe.certificado import Certificado
except ImportError:
    _logger.error('Cannot import pytrustnfe', exc_info=True)


STATE = {'edit': [('readonly', False)]}


class InvoiceEletronicItem(models.Model):
    _inherit = 'invoice.eletronic.item'

    codigo_tributacao_municipio = fields.Char(
        string=u"Cód. Tribut. Munic.", size=20, readonly=True,
        help="Código de Tributação no Munípio", states=STATE)


class InvoiceEletronic(models.Model):
    _inherit = 'invoice.eletronic'

    state = fields.Selection(
        selection_add=[('waiting', 'Esperando processamento')])

    def _get_state_to_send(self):
        res = super(InvoiceEletronic, self)._get_state_to_send()
        return res + ('waiting',)

    @api.depends('valor_retencao_pis', 'valor_retencao_cofins',
                 'valor_retencao_irrf', 'valor_retencao_inss',
                 'valor_retencao_csll')
    def _compute_total_retencoes(self):
        for item in self:
            total = item.valor_retencao_pis + item.valor_retencao_cofins + \
                item.valor_retencao_irrf + item.valor_retencao_inss + \
                item.valor_retencao_csll
            item.retencoes_federais = total

    retencoes_federais = fields.Monetary(
        string="Retenções Federais", compute=_compute_total_retencoes)

    @api.multi
    def _hook_validation(self):
        errors = super(InvoiceEletronic, self)._hook_validation()
        if self.model == '002':
            issqn_codigo = ''
            if not self.company_id.inscr_mun:
                errors.append(u'Inscrição municipal obrigatória')
            if not self.company_id.cnae_main_id.code:
                errors.append(u'CNAE Principal da empresa obrigatório')
            for eletr in self.eletronic_item_ids:
                prod = u"Produto: %s - %s" % (eletr.product_id.default_code,
                                              eletr.product_id.name)
                if eletr.tipo_produto == 'product':
                    errors.append(
                        u'Esse documento permite apenas serviços - %s' % prod)
                if eletr.tipo_produto == 'service':
                    if not eletr.issqn_codigo:
                        errors.append(u'%s - Código de Serviço' % prod)
                    if not issqn_codigo:
                        issqn_codigo = eletr.issqn_codigo
                    if issqn_codigo != eletr.issqn_codigo:
                        errors.append(u'%s - Apenas itens com o mesmo código \
                                      de serviço podem ser enviados' % prod)
                    # if not eletr.codigo_tributacao_municipio:
                    #     errors.append(u'%s - %s - Código de tributação do município \
                    #     obrigatório' % (
                    #         eletr.product_id.name,
                    #         eletr.product_id.service_type_id.name))

        return errors

    @api.multi
    def _prepare_eletronic_invoice_values(self):
        res = super(InvoiceEletronic, self)._prepare_eletronic_invoice_values()
        if self.model != '002':
            return res

        tz = pytz.timezone(self.env.user.partner_id.tz) or pytz.utc
        dt_emissao = pytz.utc.localize(self.data_emissao).astimezone(tz)
        dt_emissao = dt_emissao.strftime('%d/%m/%Y')

        partner = self.commercial_partner_id
        city_tomador = partner.city_id
        #import pudb;pu.db
        #code = self._fields['metodo_pagamento'].selection    
        #code_dict = dict(code)
        #metodo_pagamento = code_dict.get(self.metodo_pagamento)
        metodo_pagamento = self.payment_mode_id.name
        
        tomador = {
            'tipo_cpfcnpj': 2 if partner.is_company else 1,
            'cnpj_cpf_destinatario': re.sub('[^0-9]', '',
                               partner.cnpj_cpf or ''),
            'im_destinatario': re.sub(
                '[^0-9]', '', partner.inscr_mun or ''),                   
            'razao_social_destinatario': partner.legal_name or partner.name,
            'endereco_destinatario': partner.street or '',
            'numero_ende_destinatario': partner.number or '',
            'complemento_ende_destinatario': partner.street2 or '',
            'bairro_destinatario': partner.district or 'Sem Bairro',
            'cep_destinatario': re.sub('[^0-9]', '', partner.zip),
            'cidade_destinatario': '%s%s' % (city_tomador.state_id.ibge_code,
                                city_tomador.ibge_code),
            'uf_destinatario': partner.state_id.code,
            "pais_destinatario": "Brasil",
            'fone_destinatario': re.sub('[^0-9]', '', partner.phone or ''),
            'email': self.partner_id.email or partner.email or '',
            

        }
        city_prestador = self.company_id.partner_id.city_id
        prestador = {
            'cnpj': re.sub(
                '[^0-9]', '', self.company_id.partner_id.cnpj_cpf or ''),
            'inscricao_municipal': re.sub(
                '[^0-9]', '', self.company_id.partner_id.inscr_mun or ''),
            'cidade': '%s%s' % (city_prestador.state_id.ibge_code,
                                city_prestador.ibge_code),
            'cnae': re.sub('[^0-9]', '', self.company_id.cnae_main_id.code),
            'razao_social': self.company_id.legal_name,
            'logradouro': self.company_id.street or '',
            'numero': self.company_id.number or '',
            'complemento': self.company_id.street2 or '',
            'bairro': self.company_id.district or 'Sem Bairro',
            'uf': self.company_id.state_id.code,
            'cep': re.sub('[^0-9]', '', self.company_id.zip),
            'telefone': re.sub('[^0-9]', '', self.company_id.phone or '')            
            
        }

        itens_servico = []
        descricao = ''
        codigo_servico = ''
        itens = ''
        for item in self.eletronic_item_ids:
            descricao = item.name
            itens += '%s - %s * %s = %s \n' %(
                item.name,
                str("%.2f" % item.quantidade),
                str("%.2f" % item.preco_unitario),
                str("%.2f" % item.valor_liquido)
            )
            itens_servico.append({
                'descricao': item.name,
                'quantidade': str("%.2f" % item.quantidade),
                'valor_unitario': str("%.2f" % item.preco_unitario),
                'valor_liquido': str("%.2f" % item.valor_liquido)
            })
            codigo_servico = str(item.codigo_tributacao_municipio)
            
            valor = self.valor_servicos - self.valor_desconto
        parcelas = ''
        parc_forma = ''
        if self.payment_term_id:       
            parc_forma = self.payment_term_id.name    
        #if self.invoice_id.num_parcela:
        #    parcelas = str(self.invoice_id.num_parcela) + ' Vezes '
        for dp in self.invoice_id.receivable_move_line_ids:
            dt = dp.date_maturity
            dta = ('%s/%s/%s') %(str(dt.day).zfill(2), str(dt.month).zfill(2), str(dt.year))        
            parcelas +=  dta  + ' ,'
        if len(metodo_pagamento + parcelas) > 40:
            parcelas = parc_forma
        desc = ''
        if self.invoice_id.name:
           desc = self.invoice_id.name 
           
        rps = {
            'cnpj_cpf_prestador': prestador['cnpj'],         
            'exterior_dest': '0',             
            'cnpj_cpf_destinatario': re.sub('[^0-9]', '',
                               partner.cnpj_cpf or ''),
            'pessoa_destinatario': 'J' if partner.is_company else 'F',
            'ie_destinatario': partner.inscr_est or '',
            'im_destinatario': re.sub(
                '[^0-9]', '', partner.inscr_mun or ''),                   
            'razao_social_destinatario': partner.legal_name or partner.name,
            'endereco_destinatario': partner.street or '',
            'numero_ende_destinatario': partner.number or '',
            'complemento_ende_destinatario': partner.street2 or '',
            'bairro_destinatario': partner.district or 'Sem Bairro',
            'cep_destinatario': re.sub('[^0-9]', '', partner.zip),
            'cidade_destinatario' : self.partner_id.city_id.name,                   
            'uf_destinatario': partner.state_id.code,
            "pais_destinatario": "Brasil",
            'fone_destinatario': re.sub('[^0-9]', '', partner.phone or ''),
            'email_destinatario': self.partner_id.email or partner.email or '',

            'valor_nf': str("%.2f" % self.valor_final),
            'deducao': '0',
            #'valor_servico': str("%.2f" % self.valor_servicos),
            'valor_servico': str("%.2f" % valor),
          
            'data_emissao': str(dt_emissao),
            'forma_de_pagamento': str(metodo_pagamento) + ' - ' + parcelas,
            'descricao': itens + ' \n \n \n \n  '  +  desc, 
            'id_codigo_servico': str(codigo_servico),
            'cancelada': 'N',
            
            'iss_retido': 'N',
            'aliq_iss': str("%.4f" % (
                self.eletronic_item_ids[0].issqn_aliquota / 100)),
            'valor_iss':  str("%.2f" % self.valor_issqn),
            
            'bc_pis': '0,00',
            'aliq_pis': '0,00',
            'valor_pis': str("%.2f" % self.valor_retencao_pis),
            
            'bc_cofins': '0,00',
            'aliq_cofins': '0,00',
            'valor_cofins': str("%.2f" % self.valor_retencao_cofins),
            'bc_csll': '0,00', 
            'aliq_csll': '0,00',
            'valor_csll': str("%.2f" % self.valor_retencao_csll),          
            

            'bc_irrf': '0,00',
            'aliq_irrf': '0,00',
            'valor_irrf': str("%.2f" % self.valor_retencao_irrf),
            'bc_inss': '0,00',
            'aliq_inss': '0,00',
            'valor_inss': str("%.2f" % self.valor_retencao_inss),          
              
            'sistema_gerador': 'ATS-Sigiss',
            'serie_rps': self.serie.code or '',
            'rps': str(self.numero),
 
        }

        res.update(rps)
        return res

    @api.multi
    def action_post_validate(self):
        super(InvoiceEletronic, self).action_post_validate()
        if self.model not in ('002'):
            return

        cert = self.company_id.with_context(
            {'bin_size': False}).nfe_a1_file
        cert_pfx = base64.decodestring(cert)

        certificado = Certificado(
            cert_pfx, self.company_id.nfe_a1_password)
        #import pudb;pu.db
        nfse_values = self._prepare_eletronic_invoice_values()
        #xml_enviar = xml_recepcionar_lote_rps(certificado, nfse=nfse_values)
        #base64.encodestring(
        self.xml_to_send = json.dumps(nfse_values)
        self.xml_to_send_name = 'nfse-enviar-%s.json' % self.numero
        arq_temp = open('/tmp/'+str(self.numero)+'.json', "w")
        arq_temp.write(json.dumps(nfse_values))
        arq_temp.close()

    def _find_attachment_ids_email(self):
        atts = super(InvoiceEletronic, self)._find_attachment_ids_email()
        if self.model not in ('002'):
            return atts

        attachment_obj = self.env['ir.attachment']
        danfe_report = self.env['ir.actions.report'].search(
            [('report_name', '=',
              'br_nfse_ginfes.main_template_br_nfse_danfe_ginfes')])
        report_service = danfe_report.xml_id
        report_name = safe_eval(danfe_report.print_report_name,
                                {'object': self, 'time': time})
        danfse, dummy = self.env.ref(report_service).render_qweb_pdf([self.id])
        filename = "%s.%s" % (report_name, "pdf")
        if danfse:
            danfe_id = attachment_obj.create(dict(
                name=filename,
                datas_fname=filename,
                datas=base64.b64encode(danfse),
                mimetype='application/pdf',
                res_model='account.invoice',
                res_id=self.invoice_id.id,
            ))
            atts.append(danfe_id.id)
        return atts

    def _novo_token(self):
        url = "https://wsconchal.sigissweb.com/rest/login"
        #headers = {"Content-Type": "application/json"}
        login = {"login": self.company_id.client_id, 
            "senha": self.company_id.user_password}
        # "hmlgc"
        response = requests.post(url, json=login)
        token = response.content
        self.company_id.sudo().write({'token_nfse': token, 
            'validade_token_nfse': datetime.now()})
        return token

    @api.multi
    def action_send_eletronic_invoice(self):
        super(InvoiceEletronic, self).action_send_eletronic_invoice()        
        if self.model != '002' or self.state in ('done', 'cancel'):
            return
        self.state = 'error'
        if not self.company_id.validade_token_nfse:
            token = self._novo_token()
        else:
            token = self.company_id.token_nfse
            token_validade = self.company_id.validade_token_nfse + timedelta(hours=11, minutes=50)
            if not self.company_id.validade_token_nfse or datetime.now() > token_validade:
                token = self._novo_token()
        #url = "https://wshml.sigissweb.com/rest/login"
        #headers = {"Content-Type": "application/json"}
        #login = {"login": "05080464000179"  , "senha":"hmlgc"}

        #response = requests.post(url, json=login)
        #token = response.content
        
        token = self.company_id.token_nfse 
        
        headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "AUTHORIZATION": token,
        }
        # "AUTHORIZATION": self.company_id.token_nfse
        # Envia o lote apenas se não existir protocolo
        if not self.recibo_nfe:

            url = "https://wsconchal.sigissweb.com/rest/nfes"

            rps = json.loads(self.xml_to_send)

            #print (rps)
            # arq_temp = open('/home/publico/clientes/safradiesel/emitidas.xml', "r")
            # rps = arq_temp.read()
            # arq_temp.close()
            # rps = json.loads(rps)

            response = requests.post(url, headers=headers, json=rps)
            numero_nota = str(self.numero) #13
            serie = self.serie.code        #'E'
            if response.status_code == 200:
                arq_temp = open('/home/ats/safradiesel/retorno.xml', "wb")
                arq_temp.write(response.content)
                arq_temp.close()
                self.nfe_processada = base64.b64encode(response.content)
                self.nfe_processada_name = "NFSe%08d.xml" % self.numero
                tree = ET.parse('/home/ats/safradiesel/retorno.xml')
                root = tree.getroot()
                for element in root.iter('numero_nf'):
                    numero_nota = element.text
                for element in root.iter('serie'):
                    serie = element.text
                        
                # enviado pegando PDF
                url = "https://wsconchal.sigissweb.com/rest/nfes/nfimpressa/%s/serie/%s" %(
                    numero_nota, serie
                )
                headers = {
                    "Content-Type": "application/pdf",
                    "AUTHORIZATION": token,
                 }
                
                response = requests.get(url, headers=headers)
                if response:
                    pdf = base64.b64encode(response.content)
                    nome_nota = 'nfse_%s_%s.pdf' %(str(numero_nota), serie)
                    attachment_obj = self.env['ir.attachment']
                    attachment_obj.create(dict(
                        name=nome_nota,
                        datas_fname=nome_nota,
                        datas=pdf,
                        mimetype='application/pdf',
                        res_model='invoice.eletronic',
                        res_id=self.id,
                    ))
                self.recibo_nfe = '%s-%s' %(str(numero_nota), serie)
                self.codigo_retorno = '100'
                self.mensagem_retorno = 'Nota enviada com sucesso'
                self.state = 'done'
                self.numero = numero_nota
            else:
                self.codigo_retorno = response.status_code
                self.mensagem_retorno = response.text
                    

    @api.multi
    def action_cancel_document(self, context=None, justificativa=None):
        if self.model not in ('002'):
            return super(InvoiceEletronic, self).action_cancel_document(
                justificativa=justificativa)
        #import pudb;pu.db
        if not justificativa:
            view_id = self.env.ref('br_nfse_sigiss.view_wizard_cancel_sigiss_nfse').id
            return {
                'name': _('Cancelamento NFE-s'),
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.cancel.nfes',
                'view_id': view_id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_edoc_id': self.id
                }
            }
                    
        #import pudb;pu.db      
                   
        # Cancelando NFEs
        #url = "https://wshml.sigissweb.com/rest/login"
        #headers = {"Content-Type": "application/json"}
        #login = {"login": "05080464000179"  , "senha":"hmlgc"}

        #response = requests.post(url, json=login)
        #token = response.content        
        #import pudb;pu.db
        if not self.company_id.validade_token_nfse:
            token = self._novo_token()
        else:  
            token = self.company_id.token_nfse
            token_validade = self.company_id.validade_token_nfse + timedelta(hours=11, minutes=50)
            if not self.company_id.validade_token_nfse or datetime.now() > token_validade:
                token = self._novo_token()

        nf = self.recibo_nfe
        numero_nota = nf[:nf.index('-')]
        serie = nf[nf.index('-')+1:len(nf)]       
        motivo = justificativa
        url = "https://wsconchal.sigissweb.com/rest/nfes/cancela/%s/serie/%s/motivo/%s" %(
            numero_nota, serie , motivo
        )
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "AUTHORIZATION": token,
        }    
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.state = 'cancel'
            self.codigo_retorno = '100'
            self.mensagem_retorno = u'Nota Fiscal de Serviço Cancelada'
        else:
            self.codigo_retorno = response.status_code
            self.mensagem_retorno = u'Erro no Cancelamento da Nota Fiscal de Serviço.' 
            raise UserError('Erro no Cancelamento da Nota Fiscal de Serviço.')
