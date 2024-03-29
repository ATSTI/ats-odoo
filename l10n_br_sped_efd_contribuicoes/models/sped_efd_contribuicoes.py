# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from unidecode import unidecode
from datetime import datetime, timedelta
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


class SpedEfdContribuicoes(models.Model):
    _name = "sped.efd.contribuicoes"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Cria o arquivo para o Sped Contribuicoes Pis/Cofins"
    _rec_name = "sped_file_name"
    _order = "date_start desc"

    date_start= fields.Date(string='Inicio de')
    date_end = fields.Date(string='até')
    tipo_escrit = fields.Selection([
        ('0', 'Original'),
        ('1', 'Retificadora'),
        ], string='Tipo Escrituração', default='0')
    cod_receita_pis = fields.Char(
        string=u"Código receita Pis(Débito DCTF)", default="810902")
    cod_receita_cofins = fields.Char(
        string=u"Código receita Cofins(Débito DCTF)", default="217201")
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
    ind_apur = fields.Selection([
        ('0', 'Mensal'),
        ('1', 'Decendial'),
        ], string='Indicador período de apuração IPI')
    cod_tipo_cont = fields.Selection([
        ('1', 'Apuração da Contribuição Exclusivamente a Alíquota Básica'),
        ('2', 'Apuração da Contribuição a Alíquotas Específicas (Diferenciadas e/ou por Unidade de Medida de Produto)'),
        ], string='Tipo de Contribuição Apurada')
    ind_reg_cum = fields.Selection([
        ('1', 'Regime de Caixa –Escrituração consolidada (Registro F500)'),
        ('2', 'Regime de Competência -Escrituração consolidada (Registro F550)'),
        ('9', 'Regime de Competência -Escrituração detalhada, com base nos registros dos Blocos “A”, “C”, “D” e “F”'),
        ], string='Critério de Escrituração e Apuração Adotado')
    contas_entrada_saida = fields.Many2many(
        comodel_name="account.account",
        string="Contas Contábeis(Saída/Receita)(0500)",
        # domain=[("user_type_id.internal_group", "=", "income")],
    )
    
    log_faturamento = fields.Text('Log de Faturamento', copy=False)
    company_id = fields.Many2one('res.company', string='Empresa', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.account'))
    sped_file = fields.Binary(string=u"Sped")
    sped_file_name = fields.Char(
        string=u"Arquivo Sped Contribuições")

    def create_file(self):
        if self.date_start > self.date_end:
            raise UserError('Erro, a data de início é maior que a data de encerramento!')
        # self.log_faturamento = 'Gerando arquivo .. <br />'
        if self.date_start and self.date_end:
            self.registro0000()
        return None

    def versao(self):
        #if fields.Datetime.from_string(self.dt_ini) >= datetime.datetime(2018, 1, 1):
        #    return '012'
        return '006'  

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

    def junta_pipe(self, registro):
        junta = ''
        for i in range(1, len(registro._valores)):
            junta = junta + '|' + registro._valores[i]
        return junta

    def registro0000(self):
        arq = ArquivoDigital()
        arq._registro_abertura.COD_VER = self.versao()
        arq._registro_abertura.TIPO_ESCRIT = 0 # 0 - Original , 1 - Retificadora
        arq._registro_abertura.DT_INI = self.date_start
        arq._registro_abertura.DT_FIN = self.date_end
        arq._registro_abertura.NOME = self.company_id.legal_name
        arq._registro_abertura.CNPJ = self.limpa_formatacao(self.company_id.cnpj_cpf)
        arq._registro_abertura.UF = self.company_id.state_id.code
        arq._registro_abertura.COD_MUN = self.company_id.city_id.ibge_code
        arq._registro_abertura.SUFRAMA = ''
        arq._registro_abertura.IND_NAT_PJ = '00' # 00 – Pessoa jurídica em geral
        arq._registro_abertura.IND_ATIV = '2' # 2 - Atividade de comércio;
        if self.company_id.accountant_id:
            contabilista = Registro0100()
            ctd = self.company_id.accountant_id
            if self.company_id.accountant_id.child_ids:
                ctd = self.company_id.accountant_id.child_ids[0]
            else:  
                msg_err = 'Cadastre o contador Pessoa Fisica dentro do Contato da Contabilidade'
                raise UserError(msg_err)
            contador = ctd.name
            contabilista.NOME = contador
            contabilista.CPF = self.limpa_formatacao(ctd.cnpj_cpf)
            contabilista.CRC = self.limpa_formatacao(ctd.crc_code)
            contabilista.END = ctd.street_name
            contabilista.CEP = self.limpa_formatacao(ctd.zip)
            contabilista.NUM = ctd.street_number
            contabilista.COMPL = ctd.street2
            contabilista.BAIRRO = ctd.district
            contabilista.FONE = self.limpa_formatacao(ctd.phone)
            contabilista.EMAIL = ctd.email
            contabilista.COD_MUN = ctd.city_id.ibge_code
            arq._blocos['0'].add(contabilista)
         
        reg110 = Registro0110()
        reg110.COD_INC_TRIB = self.cod_inc_trib #  Cód. ind. da incidência tributária
        reg110.IND_APRO_CRED = self.ind_apro_cred # Cód. ind. de método de apropriação de créditos comuns
        reg110.COD_TIPO_CONT = self.cod_tipo_cont # Cód. ind. do Tipo de Contribuição Apurada
        if self.cod_inc_trib == '2':
            reg110.IND_REG_CUM = self.ind_reg_cum # Cód. ind. do critério de escrituração e apuração adotado
        arq._blocos['0'].add(reg110)
        
        reg0140 = Registro0140()
        reg0140.COD_EST = str(self.company_id.id)
        reg0140.NOME = self.company_id.name
        reg0140.CNPJ = self.limpa_formatacao(self.company_id.cnpj_cpf)
        reg0140.UF = self.company_id.state_id.code
        reg0140.IE = self.limpa_formatacao(self.company_id.inscr_est)
        reg0140.COD_MUN = self.company_id.city_id.ibge_code
        reg0140.IM = ''
        reg0140.SUFRAMA = ''
        arq._blocos['0'].add(reg0140)            

        dt = self.date_start
        dta_s = '%s-%s-%s' %(str(dt.year),str(dt.month).zfill(2),
            str(dt.day).zfill(2))
        dt = self.date_end
        dta_e = '%s-%s-%s' %(str(dt.year),str(dt.month).zfill(2),
            str(dt.day).zfill(2))
        periodo = 'ie.company_id = %s and \
            date_trunc(\'day\', ie.document_date) \
            between \'%s\' and \'%s\'' %(str(self.company_id.id), dta_s, dta_e)
        # FORNECEDORES
        for item_lista in self.query_registro0150(periodo):
            arq.read_registro(self.junta_pipe(item_lista))

        for item_lista in self.query_registro0190(periodo):
            arq.read_registro(self.junta_pipe(item_lista))

        for item_lista in self.query_registro0200(periodo):
            arq.read_registro(self.junta_pipe(item_lista))
            """ # TODO PRECIDO DISTO ??
            # 0205 - ALTERACAO NO ITEM
            for item_alt in self.query_registro0205(item_lista.COD_ITEM):
                arq.read_registro(self.junta_pipe(item_alt))
            # 0220 - Conversão Unidade Medida
            for item_unit in self.query_registro0220(item_lista.COD_ITEM):            
                arq.read_registro(self.junta_pipe(item_unit))
            """
            
        for item_lista in self.query_registro0400(periodo):
            arq.read_registro(self.junta_pipe(item_lista))

        query = """
                    select distinct
                        ie.id, ie.state_edoc, ie.issuer
                    from
                        l10n_br_fiscal_document as ie
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc in ('autorizada', 'cancelada'))
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()

        # Registro 500
        list_cod_cta = set()
        for conta in self.contas_entrada_saida:
            list_cod_cta.add(conta.id)
   
        for id in query_resposta:
            if id[2] == 'partner' and id[1] == 'cancelada':
                continue
            
            for item_lista in self.query_registroC100(id[0]):
                if id[1] == 'autorizada':
                    nfe_line = self.env['l10n_br_fiscal.document.line'].search([
                        ('document_id','=', id[0]),
                        ], order='nfe40_nItem, id')
                    
                    # TODO - qdo nota de SAIDA mostrar conta de SAIDA
                    for line in nfe_line:
                        conta = 0
                        if line.product_id.categ_id and (
                           line.product_id.categ_id.property_stock_account_input_categ_id
                        ):
                            conta = line.product_id.categ_id.property_stock_account_input_categ_id.id
                        elif line.product_id.categ_id and (
                            line.product_id.categ_id.parent_id and
                            line.product_id.categ_id.parent_id.property_stock_account_input_categ_id
                        ):
                            conta = line.product_id.categ_id.parent_id.property_stock_account_input_categ_id.id
                        if conta not in list_cod_cta:
                            list_cod_cta.add(conta)

        conta_ids = self.env['account.account'].search([('id', 'in', list(list_cod_cta))])
        for conta in conta_ids:
            reg500 = Registro0500()
            reg500.DT_ALT = conta.write_date
            # Conta de resultado
            if conta.internal_group == "asset":
                reg500.COD_NAT_CC = '01'
            elif conta.internal_group == "liability":
                reg500.COD_NAT_CC = '02'
            elif conta.internal_group == "equity":
                reg500.COD_NAT_CC = '03'
            elif conta.internal_group == "income":
                reg500.COD_NAT_CC = '04'
            elif conta.internal_group == "expense":
                reg500.COD_NAT_CC = '04'
            # TODO Sintetica / Analitica
            reg500.IND_CTA = 'S'
            # TODO confirmar nivel
            reg500.NÍVEL = '5'
            reg500.COD_CTA = conta.code
            reg500.NOME_CTA = conta.name
            arq._blocos['0'].add(reg500)

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
            if id[2] == 'partner' and id[1] == 'cancelada':
                continue
            regC001.IND_MOV = '0'
            # TODO C100 - Notas Fiscais - Feito        
            for item_lista in self.query_registroC100(id[0]):
                arq.read_registro(self.junta_pipe(item_lista))
                # TODO C101 - DIFAL - Feito 
                #for item_lista in self.query_registroC101(self.fatura):
                #    arq.read_registro(self.junta_pipe(item_lista))

            # TODO C110 - Inf. Adiciontal
            
            # TODO C170 - Itens Nota Fiscal de Compras = Fazendo
            if id[1] == 'autorizada':
                for item_lista in self.query_registroC170(id[0]):
                    arq.read_registro(self.junta_pipe(item_lista))
                                        
        # TODO BLOCO D - prestações ou contratações de serviços 
        # de comunicação, transporte interestadual e intermunicipa
        # TODO D100 - Periodo Apuracao
        
        query = """
                    select distinct
                        ie.id, ie.state_edoc
                    from
                        l10n_br_fiscal_document as ie
                    where
                        %s
                        and (ie.document_type in ('57','67'))
                        and ((ie.amount_pis_value > 0) or (ie.amount_cofins_value > 0))
                        and (ie.state_edoc in ('autorizada'))
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        cont = 1
        registro_D001 = RegistroD001()
        if query_resposta:
            registro_D001.IND_MOV = '0'
        else:
            registro_D001.IND_MOV = '1'

        # TODO PAREI AQUI
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
        for item_lista in self.query_registroM200(periodo):
            arq.read_registro(self.junta_pipe(item_lista))

        for item_lista in self.query_registroM400(periodo):
            arq.read_registro(self.junta_pipe(item_lista))
            for item_lista in self.query_registroM410(item_lista.CST_PIS, periodo):
                arq.read_registro(self.junta_pipe(item_lista))

        # é gerados pelo VALIDADOR
        for item_lista in self.query_registroM600(periodo):
            arq.read_registro(self.junta_pipe(item_lista))
        
        
        """
        regM800 = RegistroM800()
        regM800.CST_COFINS = '06'
        #TODO VL_TOT_REC CARREGAR VALOR.
        regM800.VL_TOT_REC = '0'
        regM800.COD_CTA = '1.1.06.11.00.00'
        arq._blocos['M'].add(regM800)
        """
        for item_lista in self.query_registroM800(periodo):
            arq.read_registro(self.junta_pipe(item_lista))
            for item_lista in self.query_registroM810(item_lista.CST_COFINS, periodo):
                arq.read_registro(self.junta_pipe(item_lista))
       
        regP001 = RegistroP001()
        regP001.IND_MOV = '1'
        
        registro_1001 = Registro1001()
        registro_1001.IND_MOV = '1'
        #arq._blocos['1'].add(registro_1001)
        arq.prepare()
        data_mod = datetime.now().strftime("%d%m%y%H%M")
        mes_ano = self.date_start.strftime("%m%y")
        self.sped_file_name = f"SpedPisCofins-{mes_ano}-{data_mod}.txt"
        msg_post = f"Arquivo gerado : {self.sped_file_name}."

        self.sped_file = base64.encodebytes(bytes(arq.getstring(), 'iso-8859-1'))
        self.message_post(
            body=msg_post,
            subject=_('Geração do Sped Contribuições Pis/Cofins concluída!'),
            message_type='notification'
        )

    def query_registro0150(self, periodo):
        query = """
                    select distinct
                        ie.partner_id
                    from
                        l10n_br_fiscal_document as ie
                    where
                        %s
                        and (ie.document_type in ('55','01','57','67'))
                        and (ie.state_edoc = 'autorizada')
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for id in query_resposta:
            resposta_participante = self.env['res.partner'].browse(id[0])
            registro_0150 = registros.Registro0150()
            registro_0150.COD_PART = str(resposta_participante.id)
            registro_0150.NOME = resposta_participante.legal_name or resposta_participante.name
            cod_pais = resposta_participante.country_id.bc_code
            registro_0150.COD_PAIS = cod_pais
            cpnj_cpf = self.limpa_formatacao(resposta_participante.cnpj_cpf)
            cod_mun = resposta_participante.city_id.ibge_code
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
            if resposta_participante.street:
                registro_0150.END = resposta_participante.street.strip()
            if resposta_participante.street_number:
                registro_0150.NUM = resposta_participante.street_number.strip()
            if resposta_participante.street2:
                registro_0150.COMPL = resposta_participante.street2.strip()
            if resposta_participante.district:
                registro_0150.BAIRRO = resposta_participante.district.strip()
            lista.append(registro_0150)

        return lista

    def query_registro0190(self, periodo):
        query = """
                    select distinct
                          uom.code,
                          uom.name
                    from
                        l10n_br_fiscal_document as ie
                    inner join
                        l10n_br_fiscal_document_line as aml
                            on ie.id = aml.document_id 
                    inner join
                        uom_uom uom
                            on uom.id = aml.uom_id
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc = 'autorizada') 
						and (ie.issuer = 'partner')
                    order by 1
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        lista_un = []
        un = ''
        for id in query_resposta:
            registro_0190 = registros.Registro0190()
            unidade = id[0][:6]
            if un == unidade:
                continue 
            lista_un.append(unidade)
            registro_0190.UNID = unidade.strip()
            desc = id[1]
            if not desc:
                msg_err = 'Unidade de medida sem descricao - Un %s.' %(unidade)
                raise UserError(msg_err)
            registro_0190.DESCR = desc.strip()
            lista.append(registro_0190)
            un = unidade
        return lista

    def query_registro0200(self, periodo):
        query = """
            select distinct
                aml.product_id
            from
                l10n_br_fiscal_document as ie
            inner join
                l10n_br_fiscal_document_line as aml
                on ie.id = aml.document_id
            where
                %s
                and (ie.document_type in ('55','01'))
                and (ie.state_edoc = 'autorizada')
                and (ie.issuer = 'partner')
                """ % (periodo)
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
            lista_item.append(resposta_produto.id)
            registro_0200 = registros.Registro0200()
            cprod = resposta_produto.default_code
            registro_0200.COD_ITEM = cprod
            desc_item = resposta_produto.name.strip()
            try:
                desc_item = desc_item.encode('iso-8859-1')
                desc_item = resposta_produto.name.strip()
            except:
                desc_item = unidecode(desc_item)
            registro_0200.DESCR_ITEM = desc_item
            if resposta_produto.barcode != resposta_produto.default_code:
                registro_0200.COD_BARRA = resposta_produto.barcode
            registro_0200.UNID_INV = resposta_produto.uom_id.code.strip()[:6]
            registro_0200.TIPO_ITEM = resposta_produto.fiscal_type
            registro_0200.COD_NCM = self.limpa_formatacao(resposta_produto.ncm_id.code)
            lista.append(registro_0200)                        
        return lista

    def query_registro0400(self, periodo):
        query = """
                select distinct
                    aml.fiscal_operation_id
                from
                    l10n_br_fiscal_document as ie
                inner join
                    l10n_br_fiscal_document_line as aml
                    on aml.document_id = ie.id
                where
                    %s
                    and (ie.document_type in ('55','01'))
                    and (ie.state_edoc in ('autorizada', 'cancelada'))
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for resposta in query_resposta:
            resposta_nat = self.env['l10n_br_fiscal.operation'].browse(resposta[0])
            registro_0400 = registros.Registro0400()
            registro_0400.COD_NAT = str(resposta_nat.id)
            registro_0400.DESCR_NAT = resposta_nat.name
            lista.append(registro_0400)
        return lista        

    def transforma_valor(self, valor):
        valor = ("%.2f" % (float(valor)))
        return str(valor).replace('.', ',')

    def query_registroC100(self, doc):
        lista = []
        nfe_ids = self.env['l10n_br_fiscal.document'].browse(doc)
        for nfe in nfe_ids:    
            # removendo Emissao de Terceiros canceladas
            if nfe.issuer == "partner" and nfe.state_edoc == "cancelada":
                return True
            # Ajustes SINIEF 34/2021 e 38/2021 (01/12/2021)
            if nfe.state_edoc == "denegada":
                return True
            cancel = False
            # Obrigatorio para todos STATE_EDOC, exceto a CHV_NF-e nao obrig. INUTLIZADA
            # REG, IND_OPER,IND_EMIT, COD_MOD, COD_SIT, SER, NUM_DOC e CHV_NF-e
            registro_c100 = registros.RegistroC100()
            if nfe.fiscal_operation_type == "in":
                registro_c100.IND_OPER = "0"
            else:
                registro_c100.IND_OPER = "1"
            if nfe.issuer == "company":    
                registro_c100.IND_EMIT = "0"
            else:
                registro_c100.IND_EMIT = "1"
            registro_c100.COD_MOD = nfe.document_type_id.code
            registro_c100.SER = nfe.document_serie
            if nfe.document_key:
                registro_c100.CHV_NFE = nfe.document_key
            registro_c100.NUM_DOC = self.limpa_formatacao(str(nfe.document_number))
            if nfe.state_edoc == "cancelada":
                registro_c100.COD_SIT = "02"
                cancel = True
            elif nfe.state_edoc == "autorizada" and nfe.edoc_purpose in ("1", "4"):
                # Documento normal ou devolucao
                registro_c100.COD_SIT = "00"
            elif nfe.state_edoc == "autorizada" and nfe.edoc_purpose in ("2", "3"):
                # Documento complementar/ajuste
                registro_c100.COD_SIT = "06"
            # A partir de janeiro de 2023, os códigos de situação de documento 04 (NF-e ou CT-e denegado) e 
            # 05 (NF-e ou CT-e Numeração inutilizada) da tabela 4.1.2 - Tabela Situação do Documento serão descontinuados.
            # elif nfe.state_edoc == "denegada" and nfe.edoc_purpose == "1":
            #     registro_c100.COD_SIT = "04"
            # elif nfe.state_edoc == "inutilizada":
            #     registro_c100.COD_SIT = "05"
            #     registro_c100.SER = ""
            #     registro_c100.CHV_NFE = ""
            # if nfe.emissao_doc == '1' and not nfe.state == 'cancel' \
            #     and nfe.chave_nfe[6:20] != \
            #     self.limpa_formatacao(nfe.partner_id.company_id.cnpj_cpf):
            #     registro_c100.COD_SIT = '08'                    
            if not cancel and nfe.state_edoc not in ("inutilizada", "cancelada"):
                registro_c100.DT_DOC = nfe.document_date
                registro_c100.DT_E_S = nfe.date_in_out
                registro_c100.IND_PGTO = '1'
                # if nfe.nfe40_pag:
                #     if len(nfe.duplicata_ids) == 1:
                #         if nfe.duplicata_ids.data_vencimento == nfe.data_agendada:
                #             registro_c100.IND_PGTO = '0'
                #         else:
                #             registro_c100.IND_PGTO = '1'
                #     else:
                #         registro_c100.IND_PGTO = '1'
                # else:
                #     registro_c100.IND_PGTO = '2'
                registro_c100.VL_MERC = nfe.amount_price_gross
                registro_c100.IND_FRT = str(nfe.nfe40_modFrete)
                registro_c100.VL_FRT = nfe.amount_freight_value
                registro_c100.VL_SEG = nfe.amount_insurance_value
                registro_c100.VL_OUT_DA = nfe.amount_other_value
                registro_c100.VL_DESC = nfe.amount_discount_value
                registro_c100.VL_DOC  = nfe.amount_total
                registro_c100.VL_BC_ICMS = nfe.amount_icms_base
                registro_c100.VL_ICMS = self.transforma_valor(nfe.amount_icms_value)
                registro_c100.VL_BC_ICMS_ST = nfe.amount_icmsst_base
                registro_c100.VL_ICMS_ST = nfe.amount_icmsst_value
                registro_c100.VL_IPI = nfe.amount_ipi_value
                registro_c100.VL_PIS = nfe.amount_pis_value
                registro_c100.VL_COFINS = nfe.amount_cofins_value
                registro_c100.COD_PART = str(nfe.partner_id.id)
            lista.append(registro_c100)                
        return lista

    def query_registroC170(self, doc):
        lista = []
        nfe_line = self.env['l10n_br_fiscal.document.line'].search([
                ('document_id','=', doc),
                ], order='nfe40_nItem, id')
        n_item = 1
        for item in nfe_line:     
            registro_c170 = registros.RegistroC170()
            # saida
            registro_c170.NUM_ITEM = str(item.nfe40_nItem or n_item)
            registro_c170.COD_ITEM = item.product_id.default_code
            registro_c170.DESCR_COMPL = self.limpa_caracteres(item.name.strip())
            registro_c170.QTD = self.transforma_valor(item.fiscal_quantity)
            registro_c170.UNID = item.uom_id.code.strip()
            registro_c170.VL_DESC = item.discount_value
            registro_c170.VL_ITEM = item.fiscal_price * item.fiscal_quantity
            if item.cfop_id.stock_move:
                registro_c170.IND_MOV = "0"
            else:
                registro_c170.IND_MOV = "1"
            try:
                registro_c170.CST_ICMS = item.icms_origin + item.icms_cst_code
            except:
                msg_err = 'Sem CST no Documento Fiscal %s. \n' %(
                    str(item.product_id.default_code))
                self.log_faturamento += msg_err
            registro_c170.CFOP = str(item.cfop_id.code)
            registro_c170.COD_NAT = str(item.fiscal_operation_id.id)
            registro_c170.VL_BC_ICMS = item.icms_base
            registro_c170.ALIQ_ICMS = item.icms_percent
            registro_c170.VL_ICMS = self.transforma_valor(item.icms_value)
            registro_c170.VL_BC_ICMS_ST = item.icmsst_base
            registro_c170.ALIQ_ST = item.icmsst_percent
            registro_c170.VL_ICMS_ST = item.icmsst_value
            registro_c170.IND_APUR = self.ind_apur
            registro_c170.CST_IPI = item.ipi_cst_code
            registro_c170.VL_BC_IPI = item.ipi_base
            registro_c170.ALIQ_IPI = item.ipi_percent
            registro_c170.VL_IPI = item.ipi_value
            registro_c170.CST_PIS = item.pis_cst_code
            registro_c170.VL_BC_PIS = item.pis_base
            registro_c170.ALIQ_PIS = item.pis_percent
            registro_c170.VL_PIS = item.pis_value
            registro_c170.CST_COFINS = item.cofins_cst_code
            registro_c170.VL_BC_COFINS = item.cofins_base
            registro_c170.ALIQ_COFINS = item.cofins_percent
            registro_c170.VL_COFINS = item.cofins_value
            if item.product_id.categ_id and (
                item.product_id.categ_id.property_stock_account_input_categ_id
            ):
                registro_c170.COD_CTA = item.product_id.categ_id.property_stock_account_input_categ_id.code
            elif item.product_id.categ_id and (
                item.product_id.categ_id.parent_id and
                item.product_id.categ_id.parent_id.property_stock_account_input_categ_id
            ):
                registro_c170.COD_CTA = item.product_id.categ_id.parent_id.property_stock_account_input_categ_id.code
            
            n_item += 1
            lista.append(registro_c170)
        return lista

    # transporte
    #TODO DEIXAMOS FORA POIS NAO EXISTE NO ATS ADMIN
    def query_registroD100(self, doc):
        lista = []
        cte_ids = self.env['l10n_br_fiscal.document'].browse(doc)
        for cte in cte_ids:
            registro_d100 = registros.RegistroD100()
            if cte.tipo_operacao == 'entrada':
                registro_d100.IND_OPER = '0' # Aquisicao
            else:
                registro_d100.IND_OPER = '1' # Prestação
            if cte.emissao_doc == 2:
                registro_d100.IND_EMIT = '1' # Terceiros
            else:
                registro_d100.IND_EMIT = '0' # Propria
            registro_d100.COD_PART = str(cte.partner_id.id)
            registro_d100.COD_MOD = str(cte.model)
            if cte.tp_emiss_cte == '1':
               registro_d100.COD_SIT = '00'
            elif cte.tp_emiss_cte == '2':
               registro_d100.COD_SIT = '01'
            elif cte.tp_emiss_cte == '3':
               registro_d100.COD_SIT = '02'
            elif cte.tp_emiss_cte == '4':
               registro_d100.COD_SIT = '03'
            # elif cte.tp_emiss_cte == '5':
            #    registro_d100.COD_SIT = '04'
            # elif cte.tp_emiss_cte == '6':
            #    registro_d100.COD_SIT = '05'
            elif cte.tp_emiss_cte == '7':
               registro_d100.COD_SIT = '06'
            elif cte.tp_emiss_cte == '8':
               registro_d100.COD_SIT = '07'
            elif cte.tp_emiss_cte == '9':
               registro_d100.COD_SIT = '08'
            registro_d100.SER = cte.serie_documento
            if cte.chave_nfe:
                registro_d100.CHV_CTE = str(cte.chave_nfe)
            registro_d100.NUM_DOC = self.limpa_formatacao(str(cte.numero))
            registro_d100.DT_A_P = cte.document_date
            registro_d100.DT_DOC = cte.document_date
            registro_d100.VL_DOC = cte.valor_final
            registro_d100.VL_DESC = cte.valor_desconto
            registro_d100.IND_FRT = cte.modalidade_frete
            registro_d100.VL_SERV = cte.valor_final
            registro_d100.VL_BC_ICMS = cte.valor_bc_icms
            registro_d100.VL_ICMS = cte.valor_icms
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
                        it.icms_origin || it.icms_cst_code, cfop.code,
                        COALESCE(it.icms_percent, 0.0) as ALIQUOTA ,
                        sum(it.amount_tax_included) as VL_OPR,
                        sum(it.icms_reduction) as VL_BC_ICMS,
                        sum(it.icms_value) as VL_ICMS,
                        sum(it.icmsst_base) as VL_BC_ICMS_ST,
                        sum(it.icmsst_value) as VL_ICMS_ST,
                        it.icms_reduction as VL_RED_BC, 
                        sum(it.ipi_value) as VL_IPI               
                    from
                        l10n_br_fiscal_document ie
                    inner join
                        l10n_br_fiscal_document_line it
                        on it.document_id = ie.id
                    inner join
                        l10n_br_fiscal_cfop cfop
                        on it.cfop_id = cfop.id
                    where    
                        ie.document_type in ('57','67')
                        and ie.state_edoc = 'autorizada'
                        and ie.id = '%s'
                    group by 
                        it.icms_reduction,
                        it.icms_percent,
                        it.icms_cst_code,
                        cfop.code,
                        it.icms_origin 
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

    def query_registroM200(self, periodo):
        query = """
                    select
                        sum(det.pis_base),
                        det.pis_percent,
                        sum(det.pis_value)
                    from
                        l10n_br_fiscal_document as ie
                    inner join
                        l10n_br_fiscal_document_line as det 
                            on ie.id = det.document_id
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc = 'autorizada')
                        and det.pis_value > 0
                        and (det.pis_cst_code in ('01','02','03'))
                    group by det.pis_percent
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
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
            regM200.VL_TOT_CONT_CUM_PER = resposta[2]
            regM200.VL_RET_CUM = '0'
            regM200.VL_OUT_DED_CUM = '0'
            regM200.VL_CONT_CUM_REC = resposta[2]
            regM200.VL_TOT_CONT_REC = resposta[2]
            lista.append(regM200)

            regM205 = RegistroM205()
            regM205.NUM_CAMPO = '12'
            regM205.COD_REC = self.cod_receita_pis
            regM205.VL_DEBITO = resposta[2]
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

    def query_registroM400(self, periodo):
        query = """
                    select 
                        det.pis_cst_code,
                        sum(det.pis_base),
                        aa.code AS cod_cta
                    from
                        l10n_br_fiscal_document as ie
                    inner join
                        l10n_br_fiscal_document_line as det 
                            on ie.id = det.document_id
                    inner join
                        account_move_line aml
                            on aml.fiscal_document_line_id = det.id
                    inner join
                        account_account AS aa
                            on aa.id = aml.account_id
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc = 'autorizada')
                        and (det.pis_cst_code in ('04','06','07','08','09'))
                    group by det.pis_cst_code, aa.code
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            registro_M400 = registros.RegistroM400()
            registro_M400.CST_PIS = resposta[0]
            registro_M400.VL_TOT_REC = self.transforma_valor(resposta[1])
            registro_M400.COD_CTA = resposta[2]
            lista.append(registro_M400)
        return lista

    def query_registroM410(self, cst_pis, periodo):
        # TODO validar isso
        query = """
                    select distinct
                        det.ncm_id,
                        sum(det.valor_liquido),
                        aa.code AS cod_cta
                    from
                        l10n_br_fiscal_document as ie
                    inner join
                        l10n_br_fiscal_document_line as det 
                            on ie.id = det.document_id
                    inner join
                        account_move_line aml
                            on aml.fiscal_document_line_id = det.id
                    inner join
                        account_account AS aa
                            on aa.id = aml.account_id
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc = 'autorizada')
                        and (det.pis_cst_code = \'%s\')
                    group by det.ncm_id
                """ % (periodo, cst_pis)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            resp_ncm = self.env['l10n_br_fiscal.tax.pis.cofins'].search([
                ('ncm_id', '=', resposta[0])
            ])
            registro_M410 = registros.RegistroM410()
            if resp_ncm:
                registro_M410.NAT_REC = resp_ncm.code
            registro_M410.VL_REC = self.transforma_valor(resposta[1])
            # TODO rever esta conta
            registro_M410.COD_CTA = resposta[2]
            lista.append(registro_M410)                        
        return lista

    def query_registroM600(self, periodo):
        query = """
                    select
                        sum(det.cofins_base),
                        det.cofins_percent,
                        sum(det.cofins_value)
                    from
                        l10n_br_fiscal_document as ie
                    inner join
                        l10n_br_fiscal_document_line as det 
                            on ie.id = det.document_id
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc = 'autorizada')
                        and det.cofins_value > 0
                        and (det.cofins_cst_code in ('01','02','03'))
                    group by det.cofins_percent
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
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
            regM605.COD_REC = self.cod_receita_cofins
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

    def query_registroM800(self, periodo):
        query = """
                    select 
                        det.cofins_cst_code,
                        sum(det.cofins_base),
                        aa.code AS cod_cta
                    from
                        l10n_br_fiscal_document as ie
                    inner join
                        l10n_br_fiscal_document_line as det 
                            on ie.id = det.document_id
                    inner join
                        account_move_line aml
                            on aml.fiscal_document_line_id = det.id
                    inner join
                        account_account AS aa
                            on aa.id = aml.account_id
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc = 'autorizada')
                        and (det.cofins_cst_code in ('04','06','07','08','09'))
                    group by det.cofins_cst_code, aa.code
                """ % (periodo)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            registro_M800 = registros.RegistroM800()
            registro_M800.CST_COFINS = resposta[0]
            registro_M800.VL_TOT_REC = self.transforma_valor(resposta[1])
            registro_M800.COD_CTA = resposta[2]
            lista.append(registro_M800)
        return lista

    def query_registroM810(self, cofins_cst, periodo):
        query = """
                    select distinct
                        det.ncm_id,
                        sum(det.valor_liquido),
                        aa.code AS cod_cta
                    from
                        l10n_br_fiscal_document as ie
                    inner join
                        l10n_br_fiscal_document_line as det 
                            on ie.id = det.document_id
                    inner join
                        account_move_line aml
                            on aml.fiscal_document_line_id = det.id
                    inner join
                        account_account AS aa
                            on aa.id = aml.account_id
                    where
                        %s
                        and (ie.document_type in ('55','01'))
                        and (ie.state_edoc = 'autorizada')
                        and (det.cofins_cst_code = \'%s\')
                    group by det.ncm_id
                """ % (periodo, cofins_cst)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        lista_item = []
        cont = 1
        for resposta in query_resposta:
            registro_M810 = registros.RegistroM810()
            resp_ncm = self.env['l10n_br_fiscal.tax.pis.cofins'].search([
                ('ncm_id', '=', resposta[0])
            ])
            if resp_ncm:
                registro_M810.NAT_REC = resp_ncm.code
            registro_M810.VL_REC = self.transforma_valor(resposta[1])
            # TODO rever esta conta
            registro_M810.COD_CTA = resposta[2] 
            lista.append(registro_M810)                        
        return lista
