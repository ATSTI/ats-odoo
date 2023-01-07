# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from unicodedata import normalize 
from unidecode import unidecode
from datetime import datetime, timedelta, timezone
import pytz
import base64
from sped.efd.pis_cofins.arquivos import ArquivoDigital
from sped.efd.pis_cofins import registros
from sped.efd.pis_cofins.registros import Registro0100
from sped.efd.pis_cofins.registros import Registro0001
from sped.efd.pis_cofins.registros import Registro0110
from sped.efd.pis_cofins.registros import Registro0140
from sped.efd.pis_cofins.registros import Registro0500
from sped.efd.pis_cofins.registros import RegistroA001
from sped.efd.pis_cofins.registros import RegistroA990
from sped.efd.pis_cofins.registros import RegistroC001
from sped.efd.pis_cofins.registros import RegistroC010
from sped.efd.pis_cofins.registros import RegistroC100
from sped.efd.pis_cofins.registros import RegistroC170
from sped.efd.pis_cofins.registros import RegistroC190
from sped.efd.pis_cofins.registros import RegistroC191
from sped.efd.pis_cofins.registros import RegistroC195
from sped.efd.pis_cofins.registros import RegistroD001
from sped.efd.pis_cofins.registros import RegistroD100
from sped.efd.pis_cofins.registros import RegistroF001
from sped.efd.pis_cofins.registros import RegistroI001
from sped.efd.pis_cofins.registros import Registro9001
from sped.efd.pis_cofins.registros import RegistroM200
from sped.efd.pis_cofins.registros import RegistroM205
from sped.efd.pis_cofins.registros import RegistroM210
from sped.efd.pis_cofins.registros import RegistroM400
from sped.efd.pis_cofins.registros import RegistroM410
from sped.efd.pis_cofins.registros import RegistroM600
from sped.efd.pis_cofins.registros import RegistroM605
from sped.efd.pis_cofins.registros import RegistroM610
from sped.efd.pis_cofins.registros import RegistroM800
from sped.efd.pis_cofins.registros import RegistroM810
from sped.efd.pis_cofins.registros import RegistroP001
from sped.efd.pis_cofins.registros import Registro9900
from sped.efd.pis_cofins.registros import Registro1001
from sped.efd.pis_cofins.registros import Registro1010

#from sped.efd.pis_cofins.registros import Registro9900

g_intervalo = [ None, None ]


class SpedPisCofins(models.Model):
    _name = "sped.piscofins"
    _description = "Cria o arquivo para o Sped Pis / Cofins"
    _order = "date_start desc"

    date_start= fields.Datetime(string='Inicio de')
    date_end = fields.Datetime(string='até')
    tipo_escrit = fields.Selection([
        ('0', 'Original'),
        ('1', 'Retificadora'),
        ], string='Tipo Escrituração')
    num_rec_anterior = fields.Char(
        string=u"Número recibo anterior")    
    ind_nat_pj = fields.Selection([
        ('0', 'Sociedade empresárial geral'),
        ('1', 'Sociedade Cooperativa'),
        ('2', 'Sujeita ao PIS/Pasep exclusivamente com base na folha de salários'),
        ('3', 'Pessoa jurídica participante SCP como sócia ostensiva'),
        ('4', 'Sociedade cooperativa participante SCP como sócia ostensiva'),
        ('5', 'Sociedade em Conta de Participação - SCP'),
        ], string='Indicador natureza pessoa jurídica', default='0')
    ind_ativ = fields.Selection([
        ('0', 'Industrial ou equiparado a industrial'),
        ('1', 'Prestador de serviços'),
        ('2', 'Atividade de comércio'),
        ('3', 'Pessoas jurídicas Lei no 9.718, de 1998'),
        ('4', 'Atividade imobiliária'),
        ('9', 'Outros'),
        ], string='Indicador atividade preponderante')
    # 0110
    cod_inc_trib = fields.Selection([
        ('1', 'Escrit. oper. incid. exclus. regime não-cumulativo'),
        ('2', 'Escrit. oper. incid. exclus. regime cumulativo'),
        ('3', 'Escrit. oper. incid. regimes não-cumulativo e cumulativo'),
        ], string='Cód. incidência tributária')
    ind_apro_cred = fields.Selection([
        ('1', 'Método de Apropriação Direta'),
        ('2', 'Método de Rateio Proporcional (Receita Bruta)'),
        ], string='Método apropriação de créditos')
    cod_tipo_cont = fields.Selection([
        ('1', 'Apuração da Contribuição Exclusivamente a Alíquota Básica'),
        ('2', 'Apuração da Contribuição a Alíquotas Específicas (Diferenciadas e/ou por Unidade de Medida de Produto)'),
        ], string='Tipo de Contribuição Apurada')    
    ind_reg_cum = fields.Selection([
        ('1', 'Regime de Caixa –Escrituração consolidada (Registro F500)'),
        ('2', 'Regime de Competência -Escrituração consolidada (Registro F550)'),
        ('9', 'Regime de Competência -Escrituração detalhada, com base nos registros dos Blocos “A”, “C”, “D” e “F”'),
        ], string='Critério de Escrituração e Apuração Adotado')    
    
    log_faturamento = fields.Html('Log de Faturamento')
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.account'))
    sped_file = fields.Binary(string=u"Sped")
    sped_file_name = fields.Char(
        string=u"Arquivo Sped")
    #vl_sld_cred_ant_difal = fields.Float('Saldo Credor per. ant. Difal', default=0.0)
    #vl_sld_cred_transp_difal = fields.Float('Saldo Credor per. seguinte Difal', default=0.0)
    #vl_sld_cred_ant_fcp = fields.Float('Saldo Credor per. ant. FCP', default=0.0)
    #vl_sld_cred_transp_fcp = fields.Float('Saldo Credor per. seguinte FCP', default=0.0)


    #arq = ArquivoDigital()
    fatura = 0
    def data_atual(self):
        global g_intervalo
        tz = pytz.timezone(self.env.user.partner_id.tz) or pytz.utc
        #dt_final = datetime.strptime(self.date_end, '%Y-%m-%d %H:%M:%S')
        dt_final = pytz.utc.localize(self.date_end).astimezone(tz)
        dt_final = datetime.strftime(dt_final, '%Y-%m-%d %H:%M:%S')
        #dt_ini = datetime.strptime(self.date_start, '%Y-%m-%d %H:%M:%S')
        dt_ini = pytz.utc.localize(self.date_start).astimezone(tz)
        dt_ini = datetime.strftime(dt_ini, '%Y-%m-%d %H:%M:%S')
        g_intervalo = [ dt_ini, dt_final ]
        return g_intervalo[1:2]


    def normalize_str(self, string):
        """
        Remove special characters and strip spaces
        """
        """
        if string:
            if not isinstance(string, str):
                string = str(string, 'utf-8', 'replace')

            string = string.encode('utf-8')
            return normalize(
                'NFKD', string.decode('utf-8')).encode('ASCII', 'ignore').decode()
        return ''
        """
        return string

    @api.multi
    def create_file(self):
        #global arq
        if self.date_start > self.date_end:
            raise UserError('Erro, a data de início é maior que a data de encerramento!')
        num_mes = 1
        self.log_faturamento = 'Gerando arquivo .. <br />'
        if self.date_start and self.date_end:
            #d1 = datetime.strptime(g_intervalo[0], "%Y-%m-%d %H:%M:%S")
            #d2 = datetime.strptime(g_intervalo[1], "%Y-%m-%d %H:%M:%S")
            self.data_atual()
            d1 = g_intervalo[0] 
            d2 = g_intervalo[1] 
            # TODO estou pegando somente NFe emissao propria aqui, 
            # o correto e pegar Emissao Terceiros tbem
            inv = self.env['account.invoice'].search([
                ('date_invoice','>=',g_intervalo[0]),
                ('date_invoice','<=',g_intervalo[1]),
                ('state','in',['open','paid', 'cancel']),
                ('product_document_id.code', '=', '55'),
                ])
            self.registro0000(inv)
            if not self.log_faturamento:
                self.log_faturamento = 'Arquivo gerado com sucesso. <br />'
        return {
            "type": "ir.actions.do_nothing",
        }

    def versao(self):
        #if fields.Datetime.from_string(self.dt_ini) >= datetime.datetime(2018, 1, 1):
        #    return '012'
        return '006'

    def transforma_data(self, data):  # aaaammdd
        if not isinstance(data, datetime):
           if len(data) > 10:
               data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
           else:
               data = datetime.strptime(data, '%Y-%m-%d')

        data = '%s%s%s' %(str(data.day).zfill(2),
              str(data.month).zfill(2), str(data.year))
        return data

    def transforma_data2(self, data):  # aaaammdd
        #data = self.limpa_formatacao(data)
        #return data[6:8] + data[4:6] + data[:4]
        return datetime.strptime(data[:10], '%Y-%m-%d')   

    def limpa_caracteres(self, data):
        if data:
            replace = ['|']
            for i in replace:
                data = data.replace(i, ' ')
        return data

    def limpa_formatacao(self, data):
        if data:
            replace = ['-', ' ', '(', ')', '/', '.', ':','º']
            for i in replace:
                data = data.replace(i, '')
        return data

    def formata_cod_municipio(self, data):
        return data[:7]

    def junta_pipe(self, registro):
        junta = ''
        for i in range(1, len(registro._valores)):
            junta = junta + '|' + registro._valores[i]
        return junta

    def registro0000(self, inv):
        arq = ArquivoDigital()
        dta_e = g_intervalo[1]
        cod_mun = '%s%s' %(self.company_id.state_id.ibge_code, self.company_id.city_id.ibge_code)
        dta_s = '%s-%s-%s' %(g_intervalo[0][:4],g_intervalo[0][5:7],g_intervalo[0][8:10])
        dta_e = '%s-%s-%s' %(dta_e[:4],dta_e[5:7],dta_e[8:10])
        arq._registro_abertura.COD_VER = self.versao()
        arq._registro_abertura.TIPO_ESCRIT = 0 # 0 - Original , 1 - Retificadora
        #arq._registro_abertura.IND_SIT_ESP = 0 # 0 a 4
        #arq._registro_abertura.NUM_REC_ANTERIOR = ''
        #arq._registro_abertura.DT_INI = self.transforma_data(dta_s)
        arq._registro_abertura.DT_INI = self.date_start
        #arq._registro_abertura.DT_FIN = self.transforma_data(dta_e)
        arq._registro_abertura.DT_FIN = self.date_end
        arq._registro_abertura.NOME = self.company_id.legal_name
        arq._registro_abertura.CNPJ = self.limpa_formatacao(self.company_id.cnpj_cpf)
        arq._registro_abertura.UF = self.company_id.state_id.code
        #arq._registro_abertura.IE = self.limpa_formatacao(self.company_id.inscr_est)
        arq._registro_abertura.COD_MUN = self.formata_cod_municipio(cod_mun)
        arq._registro_abertura.SUFRAMA = ''
        arq._registro_abertura.IND_NAT_PJ = '00' # 00 – Pessoa jurídica em geral
        arq._registro_abertura.IND_ATIV = '2' # 2 - Atividade de comércio;
        #reg0001 = Registro0001()
        #if inv:
        #    reg0001.IND_MOV = '0'
        #else:
        #    reg0001.IND_MOV = '1'
        #arq._blocos['0'].add(reg0001)

        if self.company_id.accountant_id:
            contabilista = Registro0100()
            ctd = self.company_id.accountant_id
            if len(self.company_id.accountant_id.cnpj_cpf) > 14:
                if self.company_id.accountant_id.child_ids:
                    ctd = self.company_id.accountant_id.child_ids[0]
                else:  
                    msg_err = 'Cadastre o contador Pessoa Fisica dentro do Contato da Contabilidade'
                    raise UserError(msg_err)
            contador = ctd.name
            cpf = ctd.cnpj_cpf
            cod_mun = '%s%s' %(ctd.state_id.ibge_code, ctd.city_id.ibge_code)
            contabilista.NOME = contador
            contabilista.CPF = self.limpa_formatacao(cpf)
            contabilista.CRC = self.limpa_formatacao(ctd.rg_fisica)
            contabilista.END = ctd.street
            contabilista.CEP = self.limpa_formatacao(ctd.zip)
            contabilista.NUM = ctd.number
            contabilista.COMPL = ctd.street2
            contabilista.BAIRRO = ctd.district
            contabilista.FONE = self.limpa_formatacao(ctd.phone)
            contabilista.EMAIL = ctd.email
            contabilista.COD_MUN = cod_mun
            arq._blocos['0'].add(contabilista)
         
        reg110 = Registro0110()
        reg110.COD_INC_TRIB = self.cod_inc_trib # Cód. ind. da incidência tributária
        reg110.IND_APRO_CRED = self.ind_apro_cred # Cód. ind. de método de apropriação de créditos comuns
        reg110.COD_TIPO_CONT = self.cod_tipo_cont # Cód. ind. do Tipo de Contribuição Apurada
        reg110.IND_REG_CUM = self.ind_reg_cum # Cód. ind. do critério de escrituração e apuração adotado
        arq._blocos['0'].add(reg110)
        
        reg0140 = Registro0140()
        reg0140.COD_EST = str(self.company_id.id)
        reg0140.NOME = self.company_id.name
        reg0140.CNPJ = self.limpa_formatacao(self.company_id.cnpj_cpf)
        reg0140.UF = self.company_id.state_id.code
        reg0140.IE = self.limpa_formatacao(self.company_id.inscr_est)
        reg0140.COD_MUN = cod_mun
        reg0140.IM = ''
        reg0140.SUFRAMA = ''
        arq._blocos['0'].add(reg0140)            

        # FORNECEDORES
        for item_lista in self.query_registro0150():
            arq.read_registro(self.junta_pipe(item_lista))

        for item_lista in self.query_registro0190():
            arq.read_registro(self.junta_pipe(item_lista))

        for item_lista in self.query_registro0200():
            arq.read_registro(self.junta_pipe(item_lista))
            """
            # 0205 - ALTERACAO NO ITEM
            for item_alt in self.query_registro0205(item_lista.COD_ITEM):
                arq.read_registro(self.junta_pipe(item_alt))
            # 0220 - Conversão Unidade Medida
            for item_unit in self.query_registro0220(item_lista.COD_ITEM):            
                arq.read_registro(self.junta_pipe(item_unit))
            """
            
        for item_lista in self.query_registro0400():
            arq.read_registro(self.junta_pipe(item_lista))
           
        # TODO - Colocar CONTA e DESCRICAO
        dt = datetime.strptime('2017-11-01','%Y-%m-%d')
        reg500 = Registro0500()
        reg500.DT_ALT = dt
        reg500.COD_NAT_CC = '01'
        reg500.IND_CTA = 'S'
        reg500.NÍVEL = '5'
        reg500.COD_CTA = '1.1.06.11.00.00'
        reg500.NOME_CTA = 'MERCADORIA REVENDA ISENTA'
        arq._blocos['0'].add(reg500)
        
        reg500 = Registro0500()
        reg500.DT_ALT = dt
        reg500.COD_NAT_CC = '01'
        reg500.IND_CTA = 'S'
        reg500.NÍVEL = '5'
        reg500.COD_CTA = '1.1.06.05.00.00'
        reg500.NOME_CTA = 'MERCADORIA REVENDA TRIBUTADA'
        arq._blocos['0'].add(reg500)

        #regB001 = RegistroB001()
        #arq._blocos['B'].add(regB001)        
        
        query = """
                    select distinct
                        d.id, d.state, ie.emissao_doc, d.product_document_id 
                    from
                        account_invoice as d
                    inner join
                        invoice_eletronic as ie
                            on ie.invoice_id = d.id
                    left join     
                        br_account_fiscal_document fd
                            on fd.id = d.product_document_id  
                    where
                        ie.data_fatura between '%s' and '%s'
                        and (fd.code in ('55','01'))
                        and ie.state in ('done')
                        and d.fiscal_position_id is not null                     
                """ % (g_intervalo[0], g_intervalo[1])
                #        ie.data_emissao between '%s' and '%s'
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        cont = 1
        regA001 = RegistroA001()
        regA001.IND_MOV = '1'
        regA990 = RegistroA990()
        regA990.QTD_LIN_A = 1
        regC001 = RegistroC001()
        regC001.IND_MOV = '1'
        regC010 = RegistroC010()
        regC010.CNPJ = self.limpa_formatacao(self.company_id.cnpj_cpf)
        regC010.IND_ESCRI = '2'
        arq._blocos['C'].add(regC010)
        for id in query_resposta:
            if id[2] == '2' and id[1] == 'cancel':
                continue
            regC001.IND_MOV = '0'
            self.fatura = id[0]
            # TODO C100 - Notas Fiscais - Feito        
            for item_lista in self.query_registroC100(self.fatura):
                arq.read_registro(self.junta_pipe(item_lista))
                # TODO C101 - DIFAL - Feito 
                #for item_lista in self.query_registroC101(self.fatura):
                #    arq.read_registro(self.junta_pipe(item_lista))

            # TODO C110 - Inf. Adiciontal
            
            # TODO C170 - Itens Nota Fiscal de Compras = Fazendo
            for item_lista in self.query_registroC170(self.fatura):
                arq.read_registro(self.junta_pipe(item_lista))
                        
            # TODO C190 - Totalizacao por CST
            """
            for item_lista in self.query_registroC190(self.fatura):
                arq.read_registro(self.junta_pipe(item_lista))
                # TODO C191 - Totalizacao por CST
                for item_lista in self.query_registroC191(self.fatura):
                    arq.read_registro(self.junta_pipe(item_lista))
                # TODO C195 - Totalizacao por CST
                for item_lista in self.query_registroC195(self.fatura):
                    arq.read_registro(self.junta_pipe(item_lista))
            """
                
        # TODO BLOCO D - prestações ou contratações de serviços 
        # de comunicação, transporte interestadual e intermunicipa
        # TODO D100 - Periodo Apuracao

        query = """
                    select distinct
                        d.id, d.state, d.product_document_id 
                    from
                        account_invoice as d
                    inner join
                        invoice_eletronic as ie
                            on ie.invoice_id = d.id
                    left join     
                        br_account_fiscal_document fd
                            on fd.id = d.product_document_id  
                    where
                        ie.data_fatura between '%s' and '%s'
                        and (fd.code in ('57','67'))
                        and ((ie.valor_pis > 0) or (ie.valor_cofins > 0))
                        and ie.state = 'done'
                        and d.fiscal_position_id is not null                        
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        cont = 1
        registro_D001 = RegistroD001()
        if query_resposta:
            registro_D001.IND_MOV = '0'
        else:
            registro_D001.IND_MOV = '1'
        #arq._blocos['D'].add(registro_D001)

        resposta_cte = self.env['invoice.eletronic'].search([
            ('model','in',('57','67')),
            ('state', '=','done'),
            ('data_fatura','>=',g_intervalo[0]),
            ('data_fatura','<=',g_intervalo[1]),
            ])
        #for cte in resposta_cte:
            # TODO D100 - Documentos Transporte
            #TODO DEIXAMOS FORA POIS NAO EXISTE NO ATS ADMIN
            #for item_lista in self.query_registroD100(cte.invoice_id.id):
                #arq.read_registro(self.junta_pipe(item_lista))
                
            # TODO D190 - Totalizacao por CST
            #for item_lista in self.query_registroD190(cte.invoice_id.id):
            #    arq.read_registro(self.junta_pipe(item_lista))
        regF001 = RegistroF001()
        regF001.IND_MOV = '1'
            
        #regF990 = RegistroF990()
        #regF990.QTD_LIN_F = 1
        #arq._blocos['F'].add(regF001)

        regI001 = RegistroI001()
        regI001.IND_MOV = '1'
        #arq._blocos['I'].add(regI990)
            
        # é gerados pelo VALIDADOR
        for item_lista in self.query_registroM200():
            arq.read_registro(self.junta_pipe(item_lista))

        for item_lista in self.query_registroM400():
            arq.read_registro(self.junta_pipe(item_lista))
            for item_lista in self.query_registroM410(item_lista.CST_PIS):
                arq.read_registro(self.junta_pipe(item_lista))

        # é gerados pelo VALIDADOR
        for item_lista in self.query_registroM600():
            arq.read_registro(self.junta_pipe(item_lista))
        
        
        """
        regM800 = RegistroM800()
        regM800.CST_COFINS = '06'
        #TODO VL_TOT_REC CARREGAR VALOR.
        regM800.VL_TOT_REC = '0'
        regM800.COD_CTA = '1.1.06.11.00.00'
        arq._blocos['M'].add(regM800)
        """
        for item_lista in self.query_registroM800():
            arq.read_registro(self.junta_pipe(item_lista))
            for item_lista in self.query_registroM810(item_lista.CST_COFINS):
                arq.read_registro(self.junta_pipe(item_lista))
       
        regP001 = RegistroP001()
        regP001.IND_MOV = '1'
        
        #import pudb;pu.db
        registro_1001 = Registro1001()
        registro_1001.IND_MOV = '1'
        #arq._blocos['1'].add(registro_1001)
        
       
        
        # TODO Colocar no cadastro da Empresa 
        #registro_1010 = Registro1010()
        #registro_1010.IND_EXP = 'N'
        #registro_1010.IND_CCRF = 'N'
        #registro_1010.IND_COMB  = 'N'
        #registro_1010.IND_USINA = 'N'
        #registro_1010.IND_VA = 'N'
        #registro_1010.IND_EE = 'N'
        #registro_1010.IND_CART = 'N'
        #registro_1010.IND_FORM = 'N'
        #registro_1010.IND_AER = 'N'
        
        #arq._blocos['1'].add(registro_1010)        
        
        #reg9001 = Registro9001()
        #if inv:
        #    reg9001.IND_MOV = '0'
        #else:
        #    reg9001.IND_MOV = '1'
        #arq._blocos['9'].add(reg9001)
        arq.prepare()
        #self.assertEqual(txt, )
        #sped_f = codecs.open(os.path.abspath(), mode='r', encoding='utf-8')
        #with open(arq.getstring(), encoding="ISO-8859-1") as f:
        #    content = f.read()
        #content = arq.getstring().encode('ISO-8859-1', 'replace')
        self.sped_file_name =  'PisCofins-%s_%s.txt' % (g_intervalo[0][5:7],g_intervalo[0][:4])
        #self.sped_file = base64.encodestring(bytes(arq.getstring(), 'utf-8'))
        arqxx = open('/opt/odoo/novo_arquivo.txt', 'w')
        arqxx.write(arq.getstring())
        arqxx.close()
        self.sped_file = base64.encodestring(bytes(arq.getstring(), 'iso-8859-1'))
        #self.sped_file = base64.encodestring(bytes(content, 'ISO-8859-1'))
        #self.sped_file = arq.getstring()
        


    def query_registro0150(self):
        query = """
                    select distinct
                        d.partner_id
                    from
                        account_invoice as d
                    inner join
                        invoice_eletronic nf
                            on nf.invoice_id = d.id
                    left join     
                        br_account_fiscal_document fd 
                            on fd.id = d.product_document_id
                    where
                        nf.data_fatura between '%s' and '%s'       
                        and (fd.code in ('55','01','57','67'))
                        and (nf.state = 'done')
                        and d.fiscal_position_id is not null 
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for id in query_resposta:
            resposta_participante = self.env['res.partner'].browse(id[0])
            registro_0150 = registros.Registro0150()
            registro_0150.COD_PART = str(resposta_participante.id)
            registro_0150.NOME = self.normalize_str(resposta_participante.legal_name or resposta_participante.name) 
            cod_pais = resposta_participante.country_id.bc_code
            registro_0150.COD_PAIS = cod_pais
            cpnj_cpf = self.limpa_formatacao(resposta_participante.cnpj_cpf)
            cod_mun = '%s%s' %(resposta_participante.state_id.ibge_code, resposta_participante.city_id.ibge_code)
            if cod_pais == '01058':
                registro_0150.COD_MUN = self.formata_cod_municipio(cod_mun)
                if len(cpnj_cpf) == 11:
                    registro_0150.CPF = cpnj_cpf
                else:
                    registro_0150.CNPJ = cpnj_cpf
                    registro_0150.IE = self.limpa_formatacao(resposta_participante.inscr_est)
            else:
                registro_0150.COD_MUN = '9999999'
            registro_0150.SUFRAMA = self.limpa_formatacao(resposta_participante.suframa)
            registro_0150.END = self.normalize_str(resposta_participante.street)
            registro_0150.NUM = resposta_participante.number
            registro_0150.COMPL = self.normalize_str(resposta_participante.street2)
            registro_0150.BAIRRO = self.normalize_str(resposta_participante.district)
            lista.append(registro_0150)

        return lista

    def query_registro0190(self):
        query = """
                    select distinct
                        substr(UPPER(pu.name), 1,6)
                        , UPPER(pu.l10n_br_description)
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det
                            on ie.id = det.invoice_eletronic_id 
                    inner join product_product pp
                        on pp.id = det.product_id    
                    inner join product_template pt
                       on pt.id = pp.product_tmpl_id
                    inner join
                        uom_uom pu
                            on pu.id = det.uom_id or pu.id = pt.uom_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                        and ie.emissao_doc = '2'
                    order by 1
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        lista_un = []
        un = ''
        for id in query_resposta:
            registro_0190 = registros.Registro0190()
            unidade = ''
            if id[0].find('-') != -1:
                unidade = id[0][:id[0].find('-')]
            else:
                unidade = id[0]
            if unidade == 'M³':
                #import pudb;pu.db
                unidade = 'M3'
            #if id[0] == 'PARES':
            #    import pudb;pu.db
            unidade = self.normalize_str(unidade[:6])
            if un == unidade:
                continue 
            lista_un.append(unidade)
            registro_0190.UNID = unidade
            desc = self.normalize_str(id[1])
            desc = desc.strip()
            #if not desc:
            #    import pudb;pu.db
            registro_0190.DESCR = self.normalize_str(id[1])
            lista.append(registro_0190)
            un = unidade
        # adicionar Lista dos itens q tem estoque e nao estao aqui   
        context = dict(self.env.context, to_date=g_intervalo[1])
        product = self.env['product.product'].with_context(context)
        resposta_inv = product.search([]) 
        produtos = []    
        for inv in resposta_inv:
            if inv.qty_available > 0.0 and \
                inv.l10n_br_sped_type in ('00','01','02','03','04','05','06','10'): 
                produtos.append(inv.id)
        un = ''
        lista_unk = []
        for prd in produtos:
            resposta_produto = self.env['product.product'].browse(prd)
            unidade = resposta_produto.uom_id.name
            unidade = unidade.strip()
            unidade = unidade.upper()
            unidade = self.normalize_str(unidade[:6])
            #if unidade == 'SC':
            #    import pudb;pu.db
            if not resposta_produto:
                continue
            if un == resposta_produto.uom_id.name:
                continue 
            if resposta_produto.uom_id.name in lista_unk:        
                continue
            lista_unk.append(resposta_produto.uom_id.name)
            #if resposta_produto.uom_id.name.upper() == 'BR':
            #    import pudb;pu.db
            if resposta_produto.uom_id.name.upper() not in lista_un:        
                registro_0190 = registros.Registro0190()
                registro_0190.UNID = resposta_produto.uom_id.name
                registro_0190.DESCR = str(resposta_produto.uom_id.l10n_br_description)
                lista.append(registro_0190)
                un = resposta_produto.uom_id.name
        return lista

    def query_registro0200(self):
        query = """
                    select distinct
                        det.product_id
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det 
                            on ie.id = det.invoice_eletronic_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        #hash = {}
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            resposta_produto = self.env['product.product'].browse(resposta[0])
            if not resposta_produto:
                continue
            #if not (resposta_produto.codigo_unico in hash):
            lista_item.append(resposta_produto.id)
            registro_0200 = registros.Registro0200()
            #cprod = resposta_produto.default_code.replace('.','')
            cprod = resposta_produto.default_code
            registro_0200.COD_ITEM = cprod
            desc_item = resposta_produto.name.strip()
            try:
                desc_item = desc_item.encode('iso-8859-1')
                desc_item = resposta_produto.name.strip()
            except:
                desc_item = unidecode(desc_item)
            registro_0200.DESCR_ITEM = self.normalize_str(desc_item)
            if resposta_produto.barcode != resposta_produto.default_code:
                registro_0200.COD_BARRA = resposta_produto.barcode
            if resposta_produto.uom_id.name.find('-') != -1:
                unidade = resposta_produto.uom_id.name[:resposta_produto.uom_id.name.find('-')]
            else:
                unidade = resposta_produto.uom_id.name
            unidade = unidade.strip()
            unidade = unidade.upper()
            unidade = self.normalize_str(unidade[:6])
            #if unidade == 'SC':
            #    import pudb;pu.db
            registro_0200.UNID_INV = unidade[:6]
            registro_0200.TIPO_ITEM = resposta_produto.l10n_br_sped_type
            registro_0200.COD_NCM = self.limpa_formatacao(resposta_produto.fiscal_classification_id.code)
            lista.append(registro_0200)                        
        return lista

    def query_registro0205(self, item):
        lista = []
        # O valor informado deve ser menor que no campo DT_FIN do registro 0000. 
        # tem q buscar a partir do ultimo dia do mes anterior
        # pois, se alterou no ultimo dia nao entrou no arquivo anterior
        data_final = datetime.strptime(g_intervalo[1], '%Y-%m-%d %H:%M:%S')
        data_final = data_final - timedelta(days=1) 
        data_final = datetime.strftime(data_final, '%Y-%m-%d %H:%M:%S') 
        data_ini = datetime.strptime(g_intervalo[0], '%Y-%m-%d %H:%M:%S')
        data_ini = data_ini - timedelta(days=1) 
        data_ini = datetime.strftime(data_ini, '%Y-%m-%d %H:%M:%S') 
        resposta_produto = self.env['product.template.sped'].search([
            ('product_id.default_code','=',item),
            ('date_change', '>=', data_ini),
            ('date_change', '<=', data_final)
            ],limit=1,order='date_change desc')
        # 0205 - Alteracao no Item
        ultima_alteracao = data_ini
        for alterado in resposta_produto:
            # se data alteracao igual ao ultimo dia nao coloca neste arquivo
            #if (alterado.date_change[:10] == data_finaldd.date_end[:10]):
            #    continue
            ultima_mudanca = self.env['product.template.sped'].search([
                ('product_id.default_code','=',item),
                ('date_change', '<', ultima_alteracao)
                ],limit=1,order='date_change desc')
            if ultima_mudanca:
                data_inicio = ultima_mudanca.date_change
            else:
                data_inicio = alterado.product_id.create_date    
            registro_0205 = registros.Registro0205()
            desc_item = alterado.valor_anterior
            if alterado.name == 'Descrição':
                try:
                    desc_item = alterado.valor_anterior.encode('iso-8859-1')
                    desc_item = alterado.valor_anterior
                except:
                    desc_item = unidecode(alterado.valor_anterior)
                registro_0205.DESCR_ANT_ITEM = desc_item.strip()
                registro_0205.DT_INI = self.transforma_data(data_inicio)
                registro_0205.DT_FIM = self.transforma_data(alterado.date_change)
                registro_0205.COD_ANT_ITEM = ''
            if alterado.name == 'Código':
                registro_0205.DESCR_ANT_ITEM = ''
                registro_0205.DT_INI = self.transforma_data(data_inicio)
                registro_0205.DT_FIM = self.transforma_data(alterado.date_change)
                registro_0205.COD_ANT_ITEM = alterado.valor_anterior
            ultima_alteracao = alterado.date_change    
            lista.append(registro_0205)

        return lista
        
    def query_registro0400(self):
        query = """
                    select distinct
                        d.fiscal_position_id
                    from
                        account_invoice as d
                    inner join
                        invoice_eletronic as ie
                            on ie.invoice_id = d.id
                    left join
                        br_account_fiscal_document fd 
                            on fd.id = d.product_document_id
                    where
                        ie.data_fatura between '%s' and '%s'                        
                        and (ie.model in ('55','01'))
                        and ie.state in ('done')
                        and d.fiscal_position_id is not null 
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for resposta in query_resposta:
            resposta_nat = self.env['account.fiscal.position'].browse(resposta[0])
            registro_0400 = registros.Registro0400()
            registro_0400.COD_NAT = str(resposta_nat.id)
            if resposta_nat.natureza_operacao:
                registro_0400.DESCR_NAT = self.normalize_str(resposta_nat.natureza_operacao)
            lista.append(registro_0400)
        return lista        

    def transforma_valor(self, valor):
        valor = ("%.2f" % (float(valor)))
        return str(valor).replace('.', ',')
        #return valor

    def query_registroC100(self, fatura):
        lista = []
        resposta = self.env['account.invoice'].browse(self.fatura)
        nfe_ids = self.env['invoice.eletronic'].search([('invoice_id','=',self.fatura)])
        if len(nfe_ids) > 1:
            msg_err = 'A Fatura %s possui dois documentos Eletronicos, esta correto ?. <br />' %(str(resposta.number or resposta.id))
            self.log_faturamento += msg_err
        for resposta_nfe in nfe_ids:    
            if (resposta.product_document_id or resposta.state in ['open','paid','cancel']) and \
                (resposta.product_document_id.code == '55'):
                # removendo Emissao de Terceiros canceladas
                if resposta_nfe.emissao_doc == '2' and resposta.state == 'cancel':
                    return True
                cancel = False 
                registro_c100 = registros.RegistroC100()
                if resposta.fiscal_position_id.fiscal_type == 'entrada':
                    registro_c100.IND_OPER = '0'
                    #print ('ENTRADA')
                else:
                    registro_c100.IND_OPER = '1'
                    #print ('SAIDA')
                if resposta_nfe.emissao_doc == '1':    
                    registro_c100.IND_EMIT = '0'
                else:
                    registro_c100.IND_EMIT = '1'
                registro_c100.COD_MOD = (resposta.nfe_modelo or resposta.product_document_id.code).zfill(2)
                if resposta_nfe.state == 'cancel':
                    registro_c100.COD_SIT = '02'
                    cancel = True
                else:
                    registro_c100.COD_SIT = '00'
                """
                elif resposta_nfe.finalidade_emissao == '1':
                    registro_c100.COD_SIT = '00'
                elif resposta_nfe.finalidade_emissao == '2':
                    registro_c100.COD_SIT = '06'                    
                elif resposta_nfe.finalidade_emissao == '4':
                    registro_c100.COD_SIT = '00'                    
                elif resposta_nfe.state  == 'denied':
                    registro_c100.COD_SIT = '04'                    
                if resposta_nfe.chave_nfe[6:20] != self.limpa_formatacao(resposta_nfe.partner_id.cnpj_cpf):
                    registro_c100.COD_SIT = '08'
                """
                if resposta.nfe_serie:
                    registro_c100.SER = resposta.nfe_serie[:3]
                else:
                    registro_c100.SER = resposta.product_serie_id.code
                if resposta.nfe_chave:
                    if len(resposta.nfe_chave) != 44:
                        msg_err = 'Tamanho da Chave NFe invalida - Fatura %s.' %(str(resposta.number or resposta.id))
                        #raise UserError(msg_err)
                        self.log_faturamento += msg_err
                if resposta_nfe.chave_nfe:
                    if len(resposta_nfe.chave_nfe) != 44:
                        msg_err = 'Tamanho da Chave NFe invalida - Fatura %s. <br />' %(str(resposta.number or resposta.id))
                        #raise UserError(msg_err)
                        self.log_faturamento += msg_err
                registro_c100.CHV_NFE = resposta.nfe_chave or resposta_nfe.chave_nfe
                #if resposta_nfe.numero == 487769:
                registro_c100.NUM_DOC = self.limpa_formatacao(str(resposta_nfe.numero))
                #print (str(resposta_nfe.numero))
                if not cancel:
                    try:
                        #registro_c100.DT_DOC  = self.transforma_data( 
                        #    resposta_nfe.data_emissao)
                        #if resposta_nfe.data_fatura:
                        #    registro_c100.DT_E_S  = self.transforma_data( 
                        #        resposta_nfe.data_fatura)
                        #else:
                        #    registro_c100.DT_E_S  = self.transforma_data( 
                        #        resposta_nfe.data_emissao)
                        registro_c100.DT_DOC  = resposta_nfe.data_emissao
                        if resposta_nfe.data_fatura:
                            registro_c100.DT_E_S  = resposta_nfe.data_fatura
                        else:
                            registro_c100.DT_E_S  = resposta_nfe.data_emissao
                    except:
                        msg_err = 'Data Emissao Fatura %s , invalida. <br />' %(str(resposta.number or resposta.id))
                        #raise UserError(msg_err)
                        self.log_faturamento += msg_err
                       
                    if resposta.receivable_move_line_ids:
                        if len(resposta.receivable_move_line_ids) == 1:
                            if resposta.receivable_move_line_ids.date_maturity == resposta.date_invoice:
                                registro_c100.IND_PGTO = '0'
                            else:
                                registro_c100.IND_PGTO = '1'
                        else:
                            registro_c100.IND_PGTO = '1'
                    else:
                        registro_c100.IND_PGTO = '2'

                    registro_c100.VL_MERC = self.transforma_valor(resposta.total_bruto)
                    registro_c100.IND_FRT = str(int(resposta.freight_responsibility))
                    registro_c100.VL_FRT = self.transforma_valor(resposta.total_frete)
                    registro_c100.VL_SEG = self.transforma_valor(resposta.total_seguro)
                    desp = 0.0
                    if resposta.total_despesas > 0.0:
                        desp = resposta.total_despesas
                        registro_c100.VL_OUT_DA = self.transforma_valor(resposta.total_despesas)
                    elif resposta.total_despesas < -0.01:
                        desp = resposta.total_despesas
                        registro_c100.VL_DESC = self.transforma_valor(resposta.total_despesas*(-1))
                    registro_c100.VL_DOC  = self.transforma_valor(resposta.total_bruto+desp)
                    registro_c100.VL_BC_ICMS = self.transforma_valor(resposta.icms_base)
                    registro_c100.VL_ICMS = self.transforma_valor(resposta.icms_value)
                    #print (str(resposta.icms_value))
                    registro_c100.VL_BC_ICMS_ST = self.transforma_valor(resposta.icms_st_base)
                    registro_c100.VL_ICMS_ST = self.transforma_valor(resposta.icms_st_value)
                    registro_c100.VL_IPI = self.transforma_valor(resposta.ipi_value)
                    registro_c100.VL_PIS = self.transforma_valor(resposta.pis_value)
                    registro_c100.VL_COFINS = self.transforma_valor(resposta.cofins_value)
                    registro_c100.COD_PART = str(resposta.partner_id.id)
                    #registro_c100.VL_PIS_ST = 0,0
                    #registro_c100.VL_COFINS_ST = 0.0
                lista.append(registro_c100)
        return lista

    def query_registroC170(self, fatura):
        lista = []
        #cont = 1
        #for id in query_resposta:
        resposta = self.env['account.invoice'].browse(self.fatura)
        r_nfe = self.env['invoice.eletronic'].search([
            ('invoice_id','=',self.fatura),
        ])
        n_item = 1
        for nf in r_nfe:
            nfe_line = self.env['invoice.eletronic.item'].search([
                ('invoice_eletronic_id','=', nf.id),
                ], order='num_item')
            for item in nfe_line:
                registro_c170 = registros.RegistroC170()
                if item.num_item > 1:
                    registro_c170.NUM_ITEM = str(item.num_item)
                else:
                    registro_c170.NUM_ITEM = str(n_item) # str(item.num_item_xml or n_item)                
                cprod = item.product_id.default_code #.replace('.','')
                registro_c170.COD_ITEM = cprod
                registro_c170.DESCR_COMPL = self.normalize_str(self.limpa_caracteres(item.name.strip()))
                registro_c170.QTD = self.transforma_valor(item.quantidade)
                if item.uom_id.name.find('-') != -1:
                    unidade = item.uom_id.name[:item.uom_id.name.find('-')]
                else:
                    unidade = item.uom_id.name
                registro_c170.UNID = self.normalize_str(unidade[:6])
                
                desc = 0.0
                if item.outras_despesas < -0.01:
                    desc = item.outras_despesas*(-1)
                if item.desconto:
                    desc = desc + item.desconto
                registro_c170.VL_DESC = self.transforma_valor(float(desc))
                registro_c170.VL_ITEM = self.transforma_valor(item.valor_bruto-desc)
                if item.cfop in ['5922', '6922']:
                    registro_c170.IND_MOV = '1'
                else:
                    registro_c170.IND_MOV = '0'
                try:
                    registro_c170.CST_ICMS = '%s%s' %(str(item.origem), str(item.icms_cst))
                except:
                    msg_err = 'Sem CST na Fatura %s. <br />' %(str(resposta.number or resposta.id))
                    #raise UserError(msg_err)
                    self.log_faturamento += msg_err
                if item.cfop:
                    registro_c170.CFOP = str(item.cfop)
                else:
                    registro_c170.CFOP = '0000'
                #if r_nfe.id == 407:
                #    import pudb;pu.db
                registro_c170.COD_NAT = str(resposta.fiscal_position_id.id)
                registro_c170.VL_BC_ICMS = self.transforma_valor(item.icms_base_calculo)
                aliq = self.env['account.invoice.line'].search([
                    ('invoice_id','=',self.fatura),
                    ('product_id','=',item.product_id.id)
                    ])
                registro_c170.ALIQ_ICMS = '0'
                for alq in aliq:
                    registro_c170.ALIQ_ICMS = self.transforma_valor(alq.icms_aliquota)
                
                registro_c170.VL_ICMS = self.transforma_valor(item.icms_valor)
                registro_c170.VL_BC_ICMS_ST = self.transforma_valor(item.icms_st_base_calculo)
                if item.icms_st_aliquota:
                    registro_c170.ALIQ_ST = self.transforma_valor(item.icms_st_aliquota)
                registro_c170.VL_ICMS_ST = self.transforma_valor(item.icms_st_valor)
                # TODO incluir na empresa o IND_APUR
                registro_c170.IND_APUR = '0'
                if not item.ipi_cst:
                    msg_err = 'Sem CST IPI na Fatura %s.' %(str(resposta.number or resposta.id))
                    raise UserError(msg_err)
                registro_c170.CST_IPI = item.ipi_cst
                #if item.codigo_enquadramento_ipi:
                #    registro_c170.COD_ENQ = item.codigo_enquadramento_ipi
                #elif item.fiscal_classification_id.codigo_enquadramento != '999':
                #    registro_c170.COD_ENQ = item.fiscal_classification_id.codigo_enquadramento
                registro_c170.VL_BC_IPI = self.transforma_valor(item.ipi_base_calculo)
                if item.ipi_aliquota:
                    registro_c170.ALIQ_IPI = self.transforma_valor(item.ipi_aliquota)
                registro_c170.VL_IPI = self.transforma_valor(item.ipi_valor)
                registro_c170.CST_PIS = item.pis_cst
                registro_c170.VL_BC_PIS = self.transforma_valor(item.pis_base_calculo)
                registro_c170.ALIQ_PIS = self.transforma_valor(item.pis_aliquota)
                #registro_c170.QUANT_BC_PIS = self.transforma_valor(
                registro_c170.VL_PIS = self.transforma_valor(item.pis_valor)
                registro_c170.CST_COFINS = item.cofins_cst
                registro_c170.VL_BC_COFINS = self.transforma_valor(item.cofins_base_calculo)
                registro_c170.ALIQ_COFINS = self.transforma_valor(item.cofins_aliquota)
                #registro_c170.QUANT_BC_COFINS = self.transforma_valor(
                registro_c170.VL_COFINS = self.transforma_valor(item.cofins_valor)
                #registro_c170.COD_CTA = 
                n_item += 1
           
                lista.append(registro_c170)

        return lista
        
    def query_registroC190(self, fatura):
        query = """
                select 
                    pp.default_code,
                    det.ncm,
                    sum(det.valor_bruto) 
                    from
                        invoice_eletronic ie
                    left join
                        invoice_eletronic_item det
                            on det.invoice_eletronic_id = ie.id
                    inner join
                        product_product pp
                            on pp.id = det.product_id
                    where 
                        ie.data_fatura between '%s' and '%s'
                        and ((ie.valor_pis > 0) or (ie.valor_cofins > 0))
                        and ie.model = '55'
                        and ie.state = 'done'
                    group by 
                        pp.default_code,
                        det.ncm
                     order by 1, 2""" %(g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        cont = 1
        for id in query_resposta:
            registro_c190 = registros.RegistroC190()
            registro_c190.COD_MOD = '55'
            dta_e = g_intervalo[1]
            dta_s = '%s-%s-%s' %(g_intervalo[0][:4],g_intervalo[0][5:7],g_intervalo[0][8:10])
            dta_e = '%s-%s-%s' %(dta_e[:4],dta_e[5:7],dta_e[8:10])
            registro_c190.DT_REF_INI = self.transforma_data(dta_s)
            registro_c190.DT_REF_FIN = self.transforma_data(dta_e)
            registro_c190.COD_ITEM = id[0]
            registro_c190.COD_NCM = self.limpa_formatacao(id[1])
            registro_c190.VL_TOT_ITEM = self.transforma_valor(float(id[2]))
            lista.append(registro_c190)

        return lista
        
    def query_registroC191(self, fatura):
        query = """
                select iei.pis_cst,
                       iei.cfop,
                       sum(iei.valor_bruto),
                       sum(iei.desconto),
                       sum(iei.pis_base_calculo),
                       iei.pis_aliquota,
                       sum(iei.pis_valor)
                    from
                        invoice_eletronic ie
                    left join
                        invoice_eletronic_item iei
                            on iei.invoice_eletronic_id = ie.id
                    where 
                        ie.data_fatura between '%s' and '%s'
                        and ((ie.valor_pis > 0) or (ie.valor_cofins > 0))
                        and ie.model = '55'
                        and ie.state = 'done'
                    group by 
                       iei.pis_cst,
                       iei.cfop,
                       iei.pis_aliquota
                     order by 1, 2""" % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        cont = 1
        for id in query_resposta:
            registro_c191 = registros.RegistroC191()
            registro_c191.CNPJ_CPF_PART = self.limpa_formatacao(self.company_id.cnpj_cpf)
            registro_c191.CFOP = id[1]
            registro_c191.CST_PIS = str(id[0]).zfill(2)
            registro_c191.VL_ITEM = self.transforma_valor(id[2])
            registro_c191.VL_DESC = self.transforma_valor(id[3])
            registro_c191.VL_BC_PIS = self.transforma_valor(id[4])
            registro_c191.ALIQ_PIS = id[5]
            registro_c191.VL_PIS = self.transforma_valor(id[6])
            #registro_c191.COD_CTA = # TODO CONTA
            lista.append(registro_c191)

        return lista

    def query_registroC195(self, fatura):
        query = """
                select iei.cofins_cst,
                       iei.cfop,
                       sum(iei.valor_bruto),
                       sum(iei.desconto),
                       sum(iei.cofins_base_calculo),
                       iei.cofins_aliquota,
                       sum(iei.cofins_valor)
                    from
                        invoice_eletronic ie
                    left join
                        invoice_eletronic_item iei
                            on iei.invoice_eletronic_id = ie.id
                    where 
                        ie.data_fatura between '%s' and '%s'
                        and ((ie.valor_pis > 0) or (ie.valor_cofins > 0))
                        and ie.model = '55'
                        and ie.state = 'done'
                    group by 
                       iei.cofins_cst,
                       iei.cfop,
                       iei.cofins_aliquota
                     order by 1, 2""" % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        cont = 1
        for id in query_resposta:
            registro_c195 = registros.RegistroC195()
            registro_c195.CNPJ_CPF_PART = self.limpa_formatacao(self.company_id.cnpj_cpf)
            registro_c195.CFOP = id[1]
            registro_c195.CST_COFINS = str(id[0]).zfill(2)
            registro_c195.VL_ITEM = self.transforma_valor(id[2])
            registro_c195.VL_DESC = self.transforma_valor(id[3])
            registro_c195.VL_BC_COFINS = self.transforma_valor(id[4])
            registro_c195.ALIQ_COFINS = id[5]
            registro_c195.VL_COFINS = self.transforma_valor(id[6])
            #registro_c195.COD_CTA = # TODO CONTA
            lista.append(registro_c195)

        return lista
        
    # transporte
    #TODO DEIXAMOS FORA POIS NAO EXISTE NO ATS ADMIN
    def query_registroD100(self, fatura):
        lista = []
        resposta_cte = self.env['account.invoice'].browse(fatura)
        for resposta in resposta_cte:
            cte = self.env['invoice.eletronic'].search([('invoice_id','=',fatura)])
            registro_d100 = registros.RegistroD100()
            registro_d100.IND_OPER = '0' # Aquisicao
            registro_d100.IND_EMIT = '1' # Terceiros
            registro_d100.COD_PART = str(resposta.partner_id.id)
            registro_d100.COD_MOD = str(resposta.nfe_modelo)  # or resposta_nfe.product_document_id.code).zfill(2)
            #if cte.tp_emiss_cte == '1':
            registro_d100.COD_SIT = '00'
            """
            elif cte.tp_emiss_cte == '2':
               registro_d100.COD_SIT = '01'
            elif cte.tp_emiss_cte == '3':
               registro_d100.COD_SIT = '02'
            elif cte.tp_emiss_cte == '4':
               registro_d100.COD_SIT = '03'
            elif cte.tp_emiss_cte == '5':
               registro_d100.COD_SIT = '04'
            elif cte.tp_emiss_cte == '6':
               registro_d100.COD_SIT = '05'
            elif cte.tp_emiss_cte == '7':
               registro_d100.COD_SIT = '06'
            elif cte.tp_emiss_cte == '8':
               registro_d100.COD_SIT = '07'
            elif cte.tp_emiss_cte == '9':
               registro_d100.COD_SIT = '08'
            """
            registro_d100.SER = resposta.nfe_serie[:3] # resposta.product_serie_id.code
            if resposta.nfe_chave:
                if len(resposta.nfe_chave) != 44:
                    msg_err = 'Tamanho da Chave NFe invalida - Fatura %s.' %(str(resposta.number or resposta.id))
                    #raise UserError(msg_err)
                    self.log_faturamento += msg_err
            registro_d100.CHV_CTE = str(resposta.nfe_chave) # or resposta_nfe.chave_nfe
            registro_d100.NUM_DOC = self.limpa_formatacao(str(cte.numero)) # or resposta_nfe.numero))
            registro_d100.DT_A_P = self.transforma_data(cte.data_fatura or resposta.date_invoice)
            registro_d100.DT_DOC = self.transforma_data(cte.data_emissao or resposta.date_invoice)
            #registro_d100.TP_CT-e = '0' # NORMAL
            registro_d100.VL_DOC = self.transforma_valor(resposta.amount_total)
            registro_d100.VL_DESC = self.transforma_valor(resposta.total_desconto)
            registro_d100.IND_FRT = '1' # Destinatario
            registro_d100.VL_SERV = self.transforma_valor(resposta.amount_total)
            registro_d100.VL_BC_ICMS = self.transforma_valor(resposta.icms_base)
            registro_d100.VL_ICMS = self.transforma_valor(resposta.icms_value)
            registro_d100.VL_NT = '0'
            registro_d100.COD_INF = ''
            registro_d100.COD_MUN_ORIG = cte.cod_mun_ini
            registro_d100.COD_MUN_DEST = cte.cod_mun_fim
            lista.append(registro_d100)

        return lista

    """ SOMENTE DE SAIDA    
    # transporte - detalhe
    def query_registroD110(self, fatura):
        lista = []
        resposta = self.env['account.invoice'].search([
            ('nfe_modelo','in',('57','67')),
            ('state', 'in',('open','paid'))
            ])
        item = 1    
        for itens in resposta.invoice_line_ids:
            registro_d110 = registros.RegistroD110()
            registro_d110.NUM_ITEM = str(item) # 
            registro_d110.COD_ITEM = itens.product_id.default_code # Terceiros
            registro_d110.VL_SERV = self.transforma_valor(itens.price_subtotal)
            registro_d110.VL_OUT = '0'
            item += 1

    # transporte - complemento
    def query_registroD120(self, fatura):
        lista = []
        resposta = self.env['account.invoice'].search([
            ('nfe_modelo','in',('57','67')),
            ('state', 'in',('open','paid'))
            ])
        item = 1    
        for itens in resposta.invoice_line_ids:
            registro_d110 = registros.RegistroD110()
            registro_d110.NUM_ITEM = str(item) # 
            registro_d110.COD_ITEM = itens.product_id.default_code # Terceiros
            registro_d110.VL_SERV = self.transforma_valor(itens.price_subtotal)
            registro_d110.VL_OUT = '0'
            item += 1
    """        

    # transporte - analitico
    def query_registroD190(self, fatura):
        query = """
                select distinct
                        pt.origin || dl.icms_cst_normal,
                        cfop.code,
                        COALESCE(at.amount, 0.0) as ALIQUOTA ,
                        sum(dl.price_subtotal+dl.outras_despesas) as VL_OPR,
                        sum(dl.icms_base_calculo) as VL_BC_ICMS,
                        sum(dl.icms_valor) as VL_ICMS,
                        sum(dl.icms_st_base_calculo) as VL_BC_ICMS_ST,
                        sum(dl.icms_st_valor) as VL_ICMS_ST,
                        case when (dl.icms_aliquota_reducao_base > 0) then
                          sum((dl.price_subtotal+dl.outras_despesas)-dl.icms_base_calculo) else 0 end as VL_RED_BC, 
                        sum(dl.ipi_valor) as VL_IPI
                    from
                        account_invoice as d
                    inner join
                        account_invoice_line dl
                            on dl.invoice_id = d.id 
                    left join
                        invoice_eletronic il
                            on il.invoice_id = d.id
                    left join
                        account_tax at
                            on at.id = dl.tax_icms_id
                    left join     
                        br_account_fiscal_document fd
                            on fd.id = d.product_document_id  
                    inner join 
                        account_fiscal_position fp 
                            on d.fiscal_position_id = fp.id
                    inner join
                        br_account_cfop cfop
                            on dl.cfop_id = cfop.id
                    inner join
                        product_product pp
                            on pp.id = dl.product_id
                    inner join
                        product_template pt
                            on pt.id = pp.product_tmpl_id
                    where    
                        d.nfe_modelo in ('57','67')
                        and d.state in ('open','paid')
                        and ((il.valor_pis > 0) or (il.valor_cofins > 0))
                        and d.fiscal_position_id is not null
                        and ((il.state is null) or (il.state = 'done'))
                        and d.id = '%s' 
                    group by 
                        dl.icms_aliquota_reducao_base,
                        dl.icms_cst_normal,
                        cfop.code,
                        at.amount,
                        pt.origin 
                    order by 1,2,3    
                """ % (fatura)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        cont = 1
        for id in query_resposta:
            registro_d190 = registros.RegistroD190()
            registro_d190.CST_ICMS = id[0]
            registro_d190.CFOP = id[1]
            registro_d190.ALIQ_ICMS = self.transforma_valor(id[2])
            registro_d190.VL_OPR = self.transforma_valor(id[3])
            registro_d190.VL_BC_ICMS = self.transforma_valor(id[4])
            registro_d190.VL_ICMS = self.transforma_valor(id[5])
            registro_d190.VL_RED_BC = self.transforma_valor(id[8])
            registro_d190.COD_OBS = ''

            lista.append(registro_d190)

        return lista

    def query_registroM200(self):
        query = """
                    select 
                        sum(det.valor_liquido),
                        det.pis_aliquota,
                        sum(det.pis_valor)
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det 
                            on ie.id = det.invoice_eletronic_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                        and det.pis_valor > 0
                        and (det.cofins_cst in ('01','02','03'))
                    group by det.pis_aliquota
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        #hash = {}
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            regM200 = RegistroM200()
            regM200.VL_TOT_CONT_NC_PER = '0'
            regM200.VL_TOT_CRED_DESC = '0'
            regM200.VL_TOT_CRED_DESC_ANT = '0'
            regM200.VL_TOT_CONT_NC_DEV = '0'
            regM200.VL_RET_NC = '0'
            regM200.VL_OUT_DED_NC = '0'
            regM200.VL_CONT_NC_REC = '0'
            regM200.VL_TOT_CONT_CUM_PER = self.transforma_valor(resposta[2])
            regM200.VL_RET_CUM = '0'
            regM200.VL_OUT_DED_CUM = '0'
            regM200.VL_CONT_CUM_REC = self.transforma_valor(resposta[2])
            regM200.VL_TOT_CONT_REC = self.transforma_valor(resposta[2])
            lista.append(regM200)

            regM205 = RegistroM205()
            regM205.NUM_CAMPO = '12'
            regM205.COD_REC = '810902'
            regM205.VL_DEBITO = self.transforma_valor(resposta[2])
            lista.append(regM205)

            regM210 = RegistroM210()
            regM210.COD_CONT = '51'
            regM210.VL_REC_BRT = self.transforma_valor(resposta[0])
            regM210.VL_BC_CONT = self.transforma_valor(resposta[0])
            regM210.VL_AJUS_ACRES_BC_PIS = '0' 
            regM210.VL_AJUS_REDUC_BC_PIS = '0'  
            regM210.VL_BC_CONT_AJUS = self.transforma_valor(resposta[0])
            regM210.ALIQ_PIS = self.transforma_valor(resposta[1])
            regM210.QUANT_BC_PIS = '0'
            regM210.ALIQ_PIS_QUANT = '0'
            regM210.VL_CONT_APUR = self.transforma_valor(resposta[2])
            regM210.VL_AJUS_ACRES = '0'
            regM210.VL_AJUS_REDUC = '0'
            regM210.VL_CONT_DIFER = '0'
            regM210.VL_CONT_DIFER_ANT = '0'
            regM210.VL_CONT_PER = self.transforma_valor(resposta[2])
            lista.append(regM210)
            
        return lista

    """


    """

    def query_registroM400(self):
        query = """
                    select 
                        det.pis_cst,
                        sum(det.valor_liquido)
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det 
                            on ie.id = det.invoice_eletronic_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                        
                        and (det.pis_cst in ('04','06','07','08','09'))
                    group by det.pis_cst
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        #hash = {}
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            registro_M400 = registros.RegistroM400()
            registro_M400.CST_PIS = resposta[0]
            registro_M400.VL_TOT_REC = self.transforma_valor(resposta[1])
            registro_M400.COD_CTA = '1.1.06.11.00.00'
            lista.append(registro_M400)
        return lista

            
    def query_registroM410(self, cst_pis):
        query = """
                    select distinct
                        substr(pr.name, 1,3),
                        sum(det.valor_liquido)
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det 
                            on ie.id = det.invoice_eletronic_id
                    inner join
                        product_product as pp
                            on pp.id = det.product_id
                    inner join
                        product_template as pt
                            on pt.id = pp.product_tmpl_id
                    inner join
                        product_category as pc
                            on pc.id = pt.categ_id
                    inner join
                        product_category as pr
                            on pr.id = pc.parent_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                        and (det.pis_cst = \'%s\')
                    group by substr(pr.name, 1,3)
                """ % (g_intervalo[0], g_intervalo[1], cst_pis)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        #hash = {}
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            registro_M410 = registros.RegistroM410()
            registro_M410.NAT_REC = resposta[0]
            registro_M410.VL_REC = self.transforma_valor(resposta[1])
            registro_M410.COD_CTA = '1.1.06.11.00.00'
            lista.append(registro_M410)                        
        return lista

    def query_registroM600(self):
        query = """
                    select
                        sum(det.valor_liquido),
                        det.cofins_aliquota,
                        sum(det.cofins_valor)
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det 
                            on ie.id = det.invoice_eletronic_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                        and (det.cofins_cst in ('01','02','03'))
                    group by det.cofins_aliquota
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        #hash = {}
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            regM600 = RegistroM600()
            regM600.VL_TOT_CONT_NC_PER = '0'
            regM600.VL_TOT_CRED_DESC = '0'
            regM600.VL_TOT_CRED_DESC_ANT = '0'
            regM600.VL_TOT_CONT_NC_DEV = '0'
            regM600.VL_RET_NC = '0'
            regM600.VL_OUT_DED_NC = '0'
            regM600.VL_CONT_NC_REC = '0'
            regM600.VL_TOT_CONT_CUM_PER = self.transforma_valor(resposta[2])
            regM600.VL_RET_CUM = '0'
            regM600.VL_OUT_DED_CUM = '0'
            regM600.VL_CONT_CUM_REC = self.transforma_valor(resposta[2])
            regM600.VL_TOT_CONT_REC = self.transforma_valor(resposta[2])
            lista.append(regM600)

            regM605 = RegistroM605()
            regM605.NUM_CAMPO = '12'
            regM605.COD_REC = '217201'
            regM605.VL_DEBITO = self.transforma_valor(resposta[2])
            lista.append(regM605)

            regM610 = RegistroM610()
            regM610.COD_CONT = '51'
            regM610.VL_REC_BRT = self.transforma_valor(resposta[0])
            regM610.VL_BC_CONT = self.transforma_valor(resposta[0])
            regM610.VL_AJUS_ACRES_BC_COFINS = '0' 
            regM610.VL_AJUS_REDUC_BC_COFINS = '0'  
            regM610.VL_BC_CONT_AJUS = self.transforma_valor(resposta[0])
            regM610.ALIQ_COFINS = self.transforma_valor(resposta[1])
            regM610.QUANT_BC_COFINS = '0'
            regM610.ALIQ_COFINS_QUANT = '0'
            regM610.VL_CONT_APUR = self.transforma_valor(resposta[2])
            regM610.VL_AJUS_ACRES = '0'
            regM610.VL_AJUS_REDUC = '0'
            regM610.VL_CONT_DIFER = '0'
            regM610.VL_CONT_DIFER_ANT = '0'
            regM610.VL_CONT_PER = self.transforma_valor(resposta[2])
            lista.append(regM610)
        return lista

    def query_registroM800(self):
        query = """
                    select 
                        det.cofins_cst,
                        sum(det.valor_liquido)
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det 
                            on ie.id = det.invoice_eletronic_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                        and (det.cofins_cst in ('04','06','07','08','09'))
                    group by det.cofins_cst
                """ % (g_intervalo[0], g_intervalo[1])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        #hash = {}
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            registro_M800 = registros.RegistroM800()
            registro_M800.CST_COFINS = resposta[0]
            registro_M800.VL_TOT_REC = self.transforma_valor(resposta[1])
            registro_M800.COD_CTA = '1.1.06.11.00.00'
            lista.append(registro_M800)
        return lista

    def query_registroM810(self, cofins_cst):
        query = """
                    select 
                        substr(pr.name,1,3),
                        sum(det.valor_liquido)
                    from
                        invoice_eletronic as ie
                    inner join
                        invoice_eletronic_item as det 
                            on ie.id = det.invoice_eletronic_id
                    inner join
                        product_product as pp
                            on pp.id = det.product_id
                    inner join
                        product_template as pt
                            on pt.id = pp.product_tmpl_id
                    inner join
                        product_category as pc
                            on pc.id = pt.categ_id
                    inner join
                        product_category as pr
                            on pr.id = pc.parent_id
                    where
                        ie.data_fatura between '%s' and '%s' 
                        and (ie.model in ('55','01'))
                        and ie.state = 'done'
                        and (det.cofins_cst = \'%s\')
                    group by substr(pr.name,1,3)
                """ % (g_intervalo[0], g_intervalo[1], cofins_cst)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        #hash = {}
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            registro_M810 = registros.RegistroM810()
            cod_nat = resposta[0]
            registro_M810.NAT_REC = cod_nat[:3]
            registro_M810.VL_REC = self.transforma_valor(resposta[1])
            registro_M810.COD_CTA = '1.1.06.11.00.00'
            lista.append(registro_M810)                        
        return lista
