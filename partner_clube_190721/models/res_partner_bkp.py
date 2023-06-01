# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
from . import atscon as con


class ResPartner(models.Model):
    _inherit = 'res.partner'

    data_nascimento = fields.Date('Data Nascimento')
    data_admissao = fields.Date(string='Data Admissão')
    data_desligamento = fields.Date(string='Data Desligamento')
    dependente = fields.Boolean(string="Dependente")
    inadimplente = fields.Boolean(string="Inadimplente")
    conselheiro = fields.Boolean(string="Conselheiro")
    funcionario = fields.Boolean(string="Funcionario")
    diretor = fields.Boolean(string="Diretor")
    pagante = fields.Boolean(string="Pagante")
    empresa = fields.Char(string='Empresa', size=50)
    fone_comercial = fields.Char(string='Fone Comercial', size=20)
    profissao = fields.Char(string='Profissao', size=50)
    pai = fields.Char(string='Pai', size=50)
    mae = fields.Char(string='Mãe', size=50)
    naturalidade = fields.Char(string='Naturalidade', size=80)
    nacionalidade = fields.Char(string='Nacionalidade', size=30)
    categoria = fields.Selection([
        ('1', 'Familiar'),
        ('2', 'Individual'),
        ('3', 'Estudante'),
        ('4', 'Benemérito'), 
        ('5', 'Atleta Militante'),
        ('9', 'Visitante'),
        ], 'Categoria')
    estado_civil = fields.Selection([
        ('S', 'Solteiro'),
        ('C', 'Casado'),
        ('U', 'União Civil'),
        ('D', 'Divorciado'), 
        ('V', 'Viúvo'),
        ('X', 'XXXXX'),
        ('Z', 'ZZZZ'),
        ], 'Estado Civil')
    parentesco = fields.Selection([
        ('A', 'Afilhada(o)'),
        ('B', 'Amasiada(o)'), 
        ('C', 'Companheira(o)'),
        ('D', 'Cônjuge'),
        ('E', 'Enteada(o)'),
        ('G', 'Ex-Cônjuge'),
        ('F', 'Filha(o)'),
        ('I', 'Irmã(o)'),
        ('N', 'Neta(o)'),
        ('P', 'Pais'),
        ('S', 'Sobrinha(o)'),
        ('R', 'Sogra(o)'),
        ], 'Parentesco')
        
    sexo = fields.Selection([
        ('F', 'Feminino'),
        ('M', 'Masculino')], 'Sexo')
    chave_acesso = fields.Char(string="Carteirinha")

    def cron_integra_clientes(self):
        self.action_atualiza_clientes(ses, False)

    def action_atualiza_clientes(self, session, cliente_n):  
        db = con.Conexao('192.168.0.50', 'C:\home\bd\db_geral.fdb')
        msg_erro = ''
        msg_sis = 'Integrando Clientes para o PDV<br>'
        hj = datetime.now()
        hj = hj - timedelta(days=3)
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        cliente = self.env['res.partner']
        
        # inativos 
        cli_ids = cliente.search([('write_date', '>=', hj), ('customer','=', True), ('active','=',False)])
        for partner_id in cli_ids:
            nome = partner_id.name.strip()
            nome = nome.replace("'"," ")
            nome = unidecode(nome)            
            sqlc = 'select codcliente from clientes where codcliente = %s' %(partner_id.id)
            cli = db.query(sqlc)
            if len(cli):
                altera =  'UPDATE CLIENTES SET STATUS = 0 \
                    ,NOMECLIENTE = \'%s\' \
                    WHERE CODCLIENTE = %s' %(nome, str(partner_id.id))
                retorno = db.insert(altera )
                if retorno:
                    msg_erro += 'ERRO : %s<br>' %(retorno)
        if cliente_n:
            cli_ids = cliente.search([('id', '=', cliente_n)])
        else:
            cli_ids = cliente.search([('write_date', '>=', hj), ('customer','=', True)])
        for partner_id in cli_ids:
            sqlc = 'select codcliente from clientes where codcliente = %s' %(partner_id.id)
            cli = db.query(sqlc)
            nome = partner_id.name.strip()
            nome = nome.replace("'"," ")
            nome = unidecode(nome)
            sqlc = 'select codcliente from clientes where codcliente = %s' %(partner_id.id)
            cli = db.query(sqlc)
            if len(cli):
                altera =  'UPDATE CLIENTES SET STATUS = 0 \
                    ,NOMECLIENTE = \'%s\' \
                    WHERE CODCLIENTE = %s' %(nome, str(partner_id.id))
                retorno = db.insert(altera )
                if retorno:
                    msg_erro += 'ERRO : %s<br>' %(retorno)
        if cliente_n:
            cli_ids = cliente.search([('id', '=', cliente_n)])
        else:
            cli_ids = cliente.search([('write_date', '>=', hj), ('customer','=', True)])
        for partner_id in cli_ids:
            sqlc = 'select codcliente from clientes where codcliente = %s' %(partner_id.id)
            cli = db.query(sqlc)
            nome = partner_id.name.strip()
            nome = nome.replace("'"," ")
            nome = unidecode(nome)
            
            if partner_id.legal_name:
                razao = partner_id.legal_name.strip()
                razao = razao.replace("'"," ")
                razao = unidecode(razao)
            else:
                razao = nome
            if not len(cli):
                tipo = '0'
                if partner_id.is_company:
                    tipo = '1'
                vendedor = '1'
                if partner_id.user_id.id:
                    vendedor = str(partner_id.user_id.id)
                ie = ''
                if partner_id.inscr_est:
                    ie = partner_id.inscr_est
                fiscal = 'J'
                
                regiao = '0'
                if partner_id.curso:
                    regiao = '1'
                insere = 'insert into clientes (\
                            CODCLIENTE, NOMECLIENTE, RAZAOSOCIAL,\
                            TIPOFIRMA,CNPJ, INSCESTADUAL,\
                            SEGMENTO, REGIAO, LIMITECREDITO,\
                            DATACADASTRO, CODUSUARIO, STATUS, CODBANCO, CODFISCAL)\
                            values (%s, \'%s\', \'%s\',\
                            %s, \'%s\',\'%s\',\
                            %s, %s, %s,\
                            %s, %s, %s, %s, \'%s\')'\
                            %(str(partner_id.id), nome, razao, \
                            tipo, partner_id.cnpj_cpf, ie,\
                            '1', regiao, '0.0',\
                            'current_date', vendedor, '1', '1', fiscal)
                retorno = db.insert(insere)
                if retorno:
                    msg_erro += 'ERRO : %s<br>' %(retorno)                
                
                fone = 'Null'
                ddd = 'Null'
                if partner_id.phone:
                    fone = '''%s''' %(partner_id.phone[4:])
                    ddd = '''%s''' %(partner_id.phone[1:3])
                fone1 = 'Null'
                ddd1 = 'Null'
                if partner_id.mobile:
                    fone1 = '''%s''' %(partner_id.mobile[4:])
                    ddd1 = partner_id.mobile[1:3]
                fone2 = 'Null'
                ddd2 = 'Null'
                if partner_id.fax:
                    fone2 = partner_id.fax[4:]
                    ddd2 = partner_id.fax[1:3]
                #buscar Cidade/UF/Pais
                cidade = 'Null'
                ibge = 'Null'
                uf = 'Null'
                pais = 'Null'
                if partner_id.city_id:
                    cidade = partner_id.city_id.name[:39]
                    if partner_id.city_id.ibge_code:
                        ibge = '%s%s-%s' %(partner_id.city_id.state_id.ibge_code, \
                                      partner_id.city_id.ibge_code[:4], \
                                      partner_id.city_id.ibge_code[4:])
                    uf = partner_id.city_id.state_id.code
                    pais = partner_id.city_id.state_id.country_id.name
                endereco = 'Null'
                if partner_id.street:
                    endereco = partner_id.street[:49]
                bairro = 'Null'
                if partner_id.district:
                    bairro = partner_id.district[:29]
                complemento = 'Null'
                if partner_id.street2:
                    complemento = partner_id.street2[:29]
                cep = 'Null'
                if partner_id.zip:
                    cep = '%s-%s' %(partner_id.zip[:5], \
                                    partner_id.zip[5:])
                    cep = cep[:10]
                email = 'Null'
                if partner_id.email:
                    email = partner_id.email[:255]
                obs = 'Null'
                if partner_id.comment:
                    obs = partner_id.comment[:199]
                numero = 'Null'
                if partner_id.number:
                    numero = partner_id.number[:5]
                inserir = 'INSERT INTO ENDERECOCLIENTE (CODENDERECO, \
                          CODCLIENTE, LOGRADOURO, BAIRRO, COMPLEMENTO,\
                          CIDADE, UF, CEP, TELEFONE, TELEFONE1, TELEFONE2,\
                          E_MAIL, TIPOEND,\
                          DADOSADICIONAIS, DDD, DDD1, DDD2,\
                          NUMERO, CD_IBGE, PAIS) VALUES ('
                inserir += str(partner_id.id)
                inserir += ',' + str(partner_id.id)
                if endereco != 'Null':
                    inserir += ', \'%s\'' %(str(endereco.encode('ascii', 'ignore')))
                else:
                    inserir += ', Null'
                if bairro != 'Null':
                    inserir += ', \'%s\'' % (str(bairro.encode('ascii', 'ignore')))
                else:
                    inserir += ', Null'
                if complemento != 'Null':
                    inserir += ', \'%s\'' % (str(complemento.encode('ascii', 'ignore')))
                else:
                    inserir += ', Null'
                if cidade != 'Null':
                    inserir += ', \'%s\'' % (str(cidade.encode('ascii', 'ignore')))
                else:
                    inserir += ', Null'
                if uf != 'Null':
                    inserir += ', \'%s\'' % (str(uf))
                else:
                    inserir += ', Null'
                if cep != 'Null':
                    inserir += ', \'%s\'' % (cep)
                else:
                    inserir += ', Null'
                if fone != 'Null':
                    inserir += ', \'%s\'' % (fone)
                else:
                    inserir += ', Null'
                if fone1 != 'Null':
                    inserir += ', \'%s\'' % (fone1)
                else:
                    inserir += ', Null'
                if fone2 != 'Null':
                    inserir += ', \'%s\'' % (fone2)
                else:
                    inserir += ', Null'
                if email != 'Null':
                    inserir += ', \'%s\'' % (email)
                else:
                    inserir += ', Null'
                inserir += ', 0' # tipoEnd
                if obs != 'Null':
                    inserir += ', \'%s\'' % (str(obs.encode('ascii', 'ignore')))
                else:
                    inserir += ', Null'
                if ddd != 'Null':
                    inserir += ', \'%s\'' % (ddd)
                else:
                    inserir += ', Null'
                if ddd1 != 'Null':
                    inserir += ', \'%s\'' % (ddd1)
                else:
                    inserir += ', Null'
                if ddd2 != 'Null':
                    inserir += ', \'%s\'' % (ddd2)
                else:
                    inserir += ', Null'
                if numero != 'Null':
                    inserir += ', \'%s\'' % (numero)
                else:
                    inserir += ', Null'
                if ibge != 'Null':
                    inserir += ', \'%s\'' % (ibge)
                else:
                    inserir += ', Null'
                if pais != 'Null':
                    inserir += ', \'%s\');' % (pais)
                else:
                    inserir += ', Null);'
                
                retorno = db.insert(inserir)
                if retorno:
                    msg_erro += 'ERRO : %s<br>' %(retorno)
            else:
                regiao = '0'
                if partner_id.curso:
                    regiao = '1'
                altera =  'UPDATE CLIENTES SET REGIAO = %s \
                    ,NOMECLIENTE = \'%s\', STATUS = 1 \
                    WHERE CODCLIENTE = %s' %(regiao, nome, str(partner_id.id))
                retorno = db.insert(altera )
                if retorno:
                    msg_erro += 'ERRO : %s<br>' %(retorno)
        
        msg_sis += 'Integracao Finalizada.<br>'
        return  msg_sis + '<br>' + msg_erro
