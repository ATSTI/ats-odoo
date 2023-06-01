# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from unidecode import unidecode
from io import BytesIO
from io import StringIO
from PIL import Image
#import fdb as Database
import psycopg2
from pytz import timezone

import sys
import base64


class ResPartner(models.Model):
    _inherit = 'res.partner'

    data_nascimento = fields.Date('Data Nascimento', required=True)
    age = fields.Integer(string="Idade", readonly=True, compute="_compute_age", store=True)
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
        ('6', 'Baba'),
        ('7', 'Professor'),
        ('9', 'Visitante'),
        ], 'Categoria', required=True)
    estado_civil = fields.Selection([
        ('S', 'Solteiro'),
        ('C', 'Casado'),
        ('U', 'Viúvo'),
        ('D', 'Separada'), 
        ('V', 'Divorciada'),
        ('X', 'Convivente'),
        ('Z', 'Não Informado'),
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
    cartao = fields.Char(string='Cartão acesso', size=10)
     
    # 17/12/2020
    @api.depends("data_nascimento")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.data_nascimento:
                age = relativedelta(fields.Date.today(), record.data_nascimento).years
            record.age = age

    #30/09/20 
    
    def write(self, vals):
        #partner_id = self
        # atualiza BD
        res = super(ResPartner, self).write(vals)  
        return res
                       
            
        # COLOQUEI o RETURN acima pra nao passar aqui , por enquanto
    
    
    
        sqlc = 'select id,  idDevice from USERS where idDevice = %s' %(partner_id.chave_acesso)
        con = Conexao()
        cli_fb = con.query(sqlc)        
        if self.chave_acesso:
            altera = ''
            if 'name' in vals:
                nome = vals['name'].strip()
                nome = nome.replace("'"," ")
                nome = unidecode(nome)
                altera = '\"Nome\" = \'%s\'' %(nome)
            if 'inadimplente' in vals:  
                inadimplente = 'F'
                if vals['inadimplente']:
                    inadimplente = 'T'
                 # daqui pra baixo todos os campos vao ficar desta formafo
                if altera:
                   altera += ', '                
                altera += '\"Inadimplente\" = \'%s\'' %(inadimplente)
            if 'Dependente' in vals:  
                Dependente = 'F'
                if vals['Dependente']:
                    Dependente = 'T' 
                if altera:
                   altera += ', '                
                altera += '\"Dependente\" = \'%s\'' %(Dependente)  
            if 'parentesco' in vals:  
                parentesco = 'F'
                if vals['parentesco']:
                    parentesco = 'T' 
                if altera:
                   altera += ', '                
                altera += '\"parentesco\" = \'%s\'' %(parentesco) 
                
            
            if 'data_nascimento' in vals:  
                data_nascimento = vals['data_nascimento'] 
                data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d')                
                data_nascimento = '%s-%s-%s' %(str(data_nascimento.month).zfill(2),str(data_nascimento.day).zfill(2), str(data_nascimento.year))  
                if altera:
                   altera += ', '                
                altera += '\"Data de Nascimento\" = \'%s\'' %(data_nascimento)                    
                           
            alterado_foto = 'N'
            if 'image' in vals:
                alterado_foto = 'S'

            if altera:    
                altera =  'UPDATE SOCIOS SET ' + altera + ' WHERE \"Via\" = %s' %(self.chave_acesso)
                db.insert(altera)

                
            if alterado_foto == 'S':
                sqlc = 'select  \"Codigo\" from SOCIOS where \"Via\" = %s' %(self.chave_acesso)
                cli = db.query(sqlc)
                foto = ''
                if len(cli):            
                    # deleta 
                    sqlf = 'SELECT \"Codigo\" FROM FOTOS WHERE \"Codigo\" = %s' %(str(cli[0][0]))
                    foto = db.query(sqlf)
                with open('/home/odoo/foto.jpg', 'wb') as f:
                    #f.write(base64.decodebytes(vals['image']))
          
                    f.write(base64.decodebytes(self.image))
                    #f.write(base64.decodebytes(img_data))
                   
                    
                    #ImageBase64 = vals['image']
                    #f.write(ImageBase64.encode())              
                
                f.close()    
              
                
                if foto and len(foto[0]):    
                    delete = "DELETE FROM FOTOS WHERE \"Codigo\" = " + str(foto[0][0])
                    db.cursor.execute(delete)
                    db.connection.commit()
                    with open('/home/odoo/foto.jpg', mode='rb') as f:
                        try:
                            db.cursor.execute("insert into FOTOS values (?, ?)", (str(cli[0][0]), f,))
                            #db.cursor.execute("insert into FOTOS values (?, ?)", (str(cli[0]), vals['image'],))
                        except:
                            msg_erro = 'ERRO'
                        f.close()
                        db.connection.commit()
                 
                retorno = ''                
               

            
            #\"Nome\" = \'%s\' , \"Titulo\" = \'%s\', \"Categoria\" = \'%s\', \"Via\" = \'%s\', \
            #               \"Dependente\" = \'%s\' , \"Inadimplente\" = \'%s\', \"Parentesco\" = \'%s\', \"Codigo_Titular\" = %s , \
            #               \"Data de Nascimento\" = \'%s\' \
            #             WHERE \"Via\" = %s' %(nome,partner_id.vat,partner_id.categoria,partner_id.chave_acesso,
            #                   dependente,inadimplente,parentesco,partner_id.ref,partner_id.data_nascimento,partner_id.chave_acesso)
            
        return res
    """
    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
    """    

    def cron_executa_uma_rotina(self):
        # CANCELAR FATURAS FATURADA ERRADA
        pol = self.env['payment.order.line'].search([
            ('payment_order_id', '=', 13),
            ('state', '=' ,'cancelled')])
        for pl in pol:
            ord_id = self.env['account.move.line'].browse([pl.move_line_id.id])
            inv = self.env['account.invoice'].browse([ord_id.invoice_id.id])
            if inv.state == 'open':
                inv.action_invoice_cancel_paid()

    def cron_limpa_tabela(self):
        db = con.Conexao('192.168.0.50', 'C:\\home\\bd\\db_geral.fdb')
        delete = "DELETE FROM ENTRADA_SAIDA"
        db.cursor.execute(delete)
        db.connection.commit()
 
    def cron_importa_frequencia(self):
        hj = datetime.now()
        hj = hj - timedelta(hours=16)
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        db = con.Conexao('192.168.0.50', 'C:\\home\\bd\\db_geral.fdb')
        sqle = 'select socio, dia, hora, movimento \
                from ENTRADA_SAIDA where dia > \'11.03.2020\' \
                ORDER BY dia, hora'
        ent_fb = db.query(sqle)
        entrada = self.env['controle.frequencia']
        for es in ent_fb:
            dt = es[1]
            hr = es[2]
            dt = '%s-%s-%s %s:%s:%s' %(
                str(dt.day).zfill(2), str(dt.month).zfill(2),
                str(dt.year), str(hr.hour), str(hr.minute), 
                str(hr.second)
                )
            dt = datetime.strptime(dt, '%d-%m-%Y %H:%M:%S')
            dt = dt + timedelta(hours=3)
            #tz = timezone(self.env.user.tz)
            #dt = tz.localize(dt).replace(microsecond=0).isoformat()
            prt = self.env['res.partner'].search([
                    ('chave_acesso', '=', es[0])
                    ])
            #if prt.id == 3914:
                # import pudb;pu.db
            if not prt:
                continue
            ent = entrada.search([
                ('data_frequencia', '>', hj),
                ('associado_id', '=', prt.id)
                ])
            hr = hr.hour + hr.minute/60
            dif = 0
            if ent.hora_entrada > hr:
                dif = ent.hora_entrada - hr
            else:
                dif = hr - ent.hora_entrada
            importado = False
            for et in ent:
                if et.hora_saida:
                    importado = True
                    break
                if hr == et.hora_entrada:
                    importado = True
                    break
                if hr == et.hora_saida:
                    importado = True
                    break
                # hr e menor do que hora de entrada entao nao e este
                if et.hora_entrada > hr:
                    importado = True
                    break
                if dif > 0 and dif < 0.09:
                    importado = True
                    break
            if importado:
                continue
            #if len(ent) > 1:
            if ent and ent.hora_entrada < hr:
                ent.write({'hora_saida': hr})
                continue
            vals = {}
            vals['data_frequencia'] = dt
            vals['hora_entrada'] = hr
            vals['associado_id'] = prt.id
            vals['carteirinha'] = prt.chave_acesso
            entrada.create(vals)
            
    def cron_integra_clientes(self):       
        self.action_atualiza_clientes()

    def action_cliente_inadimplente(self): 
        #db = con.Conexao('192.168.0.50', 'C:\\home\\bd\\db_geral.fdb')
        msg_erro = ''
        msg_sis = 'Socios Inadimplentes <br>'
        hj = datetime.now()
        if hj.month == 1:
            mes = 12
        else:
            mes = hj.month - 1
        hj = '%s-%s-11 12:00:01' %(
            str(hj.year), str(mes).zfill(2)
        )
        conta = self.env['account.move.line']
        conta_ids = conta.search([('reconciled', '=', False), 
            ('date_maturity', '<', hj),
            ('user_type_id.type', '=', 'receivable'),
            ('debit', '>', 0),
            ], order='partner_id')
        # altero todos no BD para Inadimplente = F
        #altera =  'UPDATE SOCIOS SET \"Inadimplente\" = \'F\''
        #retorno = db.insert(altera)
        # procurando quem esta no Odoo Inadimplente = False
        prt_ids = self.env['res.partner'].search([
            ('customer', '=', True),
            ('inadimplente', '=', True),
        ])
        for prt in prt_ids:
            #if prt.id == 2551:
            #    import pudb;pu.db
            if not prt.parent_id:
                cnt_ids = conta.search([('reconciled', '=', False), 
                    ('date_maturity', '<', hj),
                    ('user_type_id.type', '=', 'receivable'),
                    ('partner_id', '=', prt.id),
                    ('debit', '>', 0),
                ])
                if not cnt_ids:
                    prt.sudo().write({'inadimplente': False})
                    parent_ids = self.env['res.partner'].search([
                        ('parent_id', '=', prt.id),
                        ('customer', '=', True),
                        ('inadimplente', '=', True),
                    ])
                    for parent in parent_ids:
                        parent.sudo().write({'inadimplente': False})

        socio = 0
        for conta in conta_ids:
            if socio != conta.partner_id.id:
                sc = self.env['res.partner'].browse(conta.partner_id.id)
                if not sc.chave_acesso: 
                    continue
                sc.sudo().write({'inadimplente': True})
                #altera =  'UPDATE Users SET \blackList\ = \'1\' \
                #    WHERE \idDevice\ = %s' %(sc.chave_acesso)
                #retorno = db.insert(altera)
                parent_ids = self.env['res.partner'].search([
                    ('parent_id', '=', sc.id),
                    ('customer', '=', True),
                ])
                for parent in parent_ids:
                    parent.sudo().write({'inadimplente': True})               
                    #altera =  'UPDATE Users SET \blackList\ = \'1\' \
                    #    WHERE \idDevice\ = %s' %(parent.chave_acesso)
                    #retorno = db.insert(altera)
                socio = conta.partner_id.id

    def insere_cartao(self, partner_id, cartao, id_user=0):
        #if cartao == '70C8BE':
        #    import pudb;pu.db
        con = Conexao()
        if id_user == 0:
            sqlc = 'select id, idDevice, inativo, name from \
                Users where idDevice = %s \
                and deleted = 0'  %(partner_id)
            cli_fb = con.query(sqlc)
            if cli_fb[0][0]:
                id_user = cli_fb[0][0]
        try:
            number = int(cartao, 16)
        except:
            erro = 'Erro cartao %s-%s' %(cartao, partner_id)
            #print(erro)
            path_log = '/home/odoo/erro_inserecartao.log'
            with open(path_log, 'a+') as f:
                f.write(erro + '\n')
            f.close() 
            return
        # CARTAO 
        sqld = 'select id from Cards where number = %s' %(str(number))
        cli_cartao = con.query(sqld)
        if cli_cartao and cli_cartao[0][0]:
            #atualiza = 'update Cards set type = 0, number = %s \
            #    where id = %s' %(str(number), str(cli_cartao[0][0]))
            #retorno = con.insert(atualiza)
            return
    
        #q = 'BCD0C0'
        #r = int(q, 16)
        #NumberStr = 'BCD0C0'
        #Number = 12374208
        idSqlite = 'SELECT MAX(id) + 1 FROM Cards'
        id_result = con.query(idSqlite)
        #if not len(id_result):
        if not id_result[0][0]:
            id = 1
        else:
            id = id_result[0][0]
        insere = 'insert into Cards (id, idUser, type, numberStr, number) values('
        insere += str(id)
        insere += ', %s, 0, \'%s\', %s)' %( 
            id_user, cartao, str(number))
        retorno = con.insert(insere)
        #con.close()

    def insere_novo_socio(self, partner_id, nome):
        #if partner_id.id == 5007:
        #    import pudb;pu.db
        msg_erro = ''
        con = Conexao()
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
        #if partner_id.chave_acesso == '115529': 
        inadimplente = 0
        if partner_id.inadimplente:
            inadimplente = 1
                      
        e_depend = ''
        id_responsavel = 0
        if partner_id.parent_id:
            if not partner_id.parent_id.chave_acesso:
                return
            if partner_id.parent_id.inadimplente:
                inadimplente = 1
            e_depend = partner_id.parent_id.chave_acesso
            sqlc = 'select id, idDevice, inativo, name from Users where idDevice = %s' %(partner_id.chave_acesso)
            depend = con.query(sqlc)
            if depend and not len(depend):
                return
            sqlc = 'select id, idDevice, inativo, name from Users where idDevice = %s' %(e_depend)
            depend = con.query(sqlc)
            if depend and len(depend):
                id_responsavel = str(depend[0][1])
                nomeReposnsavel = partner_id.parent_id.name.strip()
                nomeReposnsavel = nomeReposnsavel.replace("'"," ")
                nomeReposnsavel = unidecode(nomeReposnsavel[:50])
            else:
                #con.close()
                return
                
             # TODO
             # colocaocmos para pegar o IdDevice do Responnsavel no campo IdResponsavel, pq  
             # quando muda o cadastro do Responsavel o sistema usa um novo ID.

        idSqlite = 'SELECT MAX(id) + 1 FROM Users'
        id_result = con.query(idSqlite)
        #if not len(id_result):
        if not id_result[0][0]:
            id_user = 1
        else:
            id_user = id_result[0][0]
        #for cli in cli_fb:
        cod = partner_id.chave_acesso
        categ = '1'
        if partner_id.categoria:
            categ = partner_id.categoria
        sql =  'INSERT INTO Users ('
        sql += 'id,name \
            ,pis,idType,idArea,contingency, deleted,admin\
            ,senha,inativo,blackList,idDevice,idResponsavel,responsavelNome\
            ,registration) values ('
        """
        outro = ',endereco,bairro, cidade, cep,cargo, \
              admissao, telefone, ramal, pai, mae, \
              nascimento, sexo, estadoCivil, nacionalidade, \
              naturalidade, idResponsavel, responsavelNome, \
              veiculo_marca, veiculo_modelo, veiculo_cor, \
              veiculo_placa,dateLimit,visitorCompany, \
              , dateStartLimit, pisAnterior,comments, \
              allowParkingSpotCompany,idArea,dataLastLog, \
              timeOfRegistration) VALUES ('
        """
        #rg = 'Null'
        #if parnter_id.rg_fisica:
        #    rg = parnter_id.rg_fisica 
        #valores = 'SELECT MAX(id) + 1 FROM Users '
        valores = str(id_user) + ','
        valores += '\'' + nome + '\''+ ', '   #_u.name, 
        valores += '0, '  
        valores += '0, 0, ' 
        valores += '0, 0, 0, ' 
        valores += '0, 0,' + str(inadimplente )+ ', '
    
        #valores += str(inadimplente)+ ', \'0\', \'0\', '
       
        valores += '\'' + cod + '\'' 
        # RESPONSAVEL
        if id_responsavel:
            valores += ',' + str(id_responsavel)
            valores += ',\'' + nomeReposnsavel + '\'' 
        else:
            valores += ', Null, Null '
        titulo = '0'
        if partner_id.vat:
            titulo = partner_id.vat
        valores += ', \'%s\'' %(titulo)
        retorno = ''
        try:
            insere = sql + valores + ')'
            #print(insere)
            retorno = con.insert(insere)
            # INSERE REGRA ACESSO
            maior_18 = '2'
            #import pudb;pu.db
            #dt = datetime.strptime('2003/06/01','%Y/%m/%d')
            #dt = datetime.strftime(datetime.today(),'%Y/%m/%d')
            dt = datetime.today() - relativedelta(years=18) # quem é menor de 18 anos
            if partner_id.data_nascimento > dt.date():
                maior_18 = '3'  # menor de idade
            idSqlite = 'SELECT MAX(id) + 1 FROM useraccessrules'
            id_result = con.query(idSqlite)
            if not id_result[0][0]:
                id_acces = 1
            else:
                id_acces = id_result[0][0]            
            insere = 'insert into useraccessrules (id, idAccessRule, idUser) values('
            insere += str(id_acces)
            insere += ', %s, %s)' %(maior_18, str(id_user))
            retorno = con.insert(insere)
            if partner_id.cartao:
                self.insere_cartao(partner_id.id, partner_id.cartao, id_user)
            
            maior18 = '1002' # esse valor vem da tabela groups
            dt = datetime.today() - relativedelta(years=18) # quem é menor de 18 anos
            if partner_id.data_nascimento > dt.date():
                maior18 = '1003'  # menor de idade esse valor vem da tabela groups
            idSql = 'SELECT MAX(id) + 1 FROM usergroups'
            id_result = con.query(idSql)
            if not id_result[0][0]:
                id_userg = 1
            else:
                id_userg = id_result[0][0]            
            inserir = 'insert into usergroups (id,idUser,idGroup,isVisitor) values('
            inserir += str(id_userg)
            inserir += ', %s, %s,0 )' %(str(id_user),maior18)
            retorno = con.insert(inserir)                
                
                
        except:
            msg_erro += 'ERRO INSERINDO SOCIOS NO IDSECURE : %s<br>' %(retorno)
            #con.close()
        if retorno:
            #import pudb;pu.db
            msg_erro += 'MSG : %s<br>' %(retorno)
        #con.close()
        return msg_erro

    def altera_socio(self, partner_id, nome):
        #import pudb;pu.db
        con = Conexao()      
        inadimplente = 0
        if partner_id.inadimplente:
            inadimplente = 1
        if partner_id.parent_id:
            if partner_id.parent_id.inadimplente:
                inadimplente = 1
        sqlc = 'select id, idDevice, inativo, name \
            from Users where idDevice = %s \
            and deleted = 0' %(partner_id.chave_acesso)
        cli_fb = con.query(sqlc)
        msg_erro = ''
        for cli in cli_fb:
            """
                ATUALIZANDO
            """
            idSqlite = 'SELECT MAX(id) + 1 FROM Users'
            id_result = con.query(idSqlite)
            add =  'UPDATE Users set name = '
            add += '\'' +  nome + '\',' 
            add += 'blackList =  %s' %(inadimplente)
            add += ' WHERE id = \'%s\'' %(cli[0]);
            retorno = con.insert(add)
             
            if retorno:
                msg_erro += 'ERRO : %s<br>' %(retorno)                
            #retorno = con.insert(add)
            if retorno:
                msg_erro += 'ERRO : %s<br>' %(retorno)
            if partner_id.cartao:
                # ve se precisa incluir o cartao
                self.insere_cartao(partner_id.chave_acesso, partner_id.cartao)
        
            #if partner_id.id == 5010:
            #    import pudb;pu.db
            #select pra ver se ja existe na tabela useraccessrules
            idSqlite = 'SELECT id FROM useraccessrules WHERE idUser = %s' %(str(cli[0]))
            ja_existe = con.query(idSqlite)
            if not ja_existe:
                dt = datetime.today() - relativedelta(years=18) 
                maior_18 = '2'  # MAIOR  ??
                if partner_id.data_nascimento > dt.date():
                    maior_18 = '3'  # menor de idade
                idSqlite = 'SELECT MAX(id) + 1 FROM useraccessrules'
                id_result = con.query(idSqlite)
                if not id_result[0][0]:
                    id_acces = 1
                else:
                    id_acces = id_result[0][0]            
                insere = 'insert into useraccessrules (id, idAccessRule, idUser) values('
                insere += str(id_acces)
                insere += ', %s, %s)' %(maior_18, str(cli[0]))
                retorno = con.insert(insere)    
        """        
                if partner_id.id == 5010:
                    import pudb;pu.db
                idSqlite = 'SELECT id FROM usergroups WHERE idUser = %s' %(str(cli[0]))
                ja_existe = con.query(idSqlite)
                if not ja_existe:
                    maior18 = '1002' # esse valor vem da tabela groups
                    dt = datetime.today() - relativedelta(years=18) # quem é menor de 18 anos
                    if partner_id.data_nascimento > dt.date():
                        maior18 = '1003'  # menor de idade esse valor vem da tabela groups
                    idSql = 'SELECT MAX(id) + 1 FROM usergroups'
                    id_result = con.query(idSql)
                    if not id_result[0][0]:
                        id_userg = 1
                    else:
                        id_userg = id_result[0][0]            
                    inserir = 'insert into usergroups (id,idUser,idGroup,isVisitor) values('
                    inserir += str(id_userg)
                    inserir += ', %s, %s,0 )' %(str(cli[0]),maior18)
                    retorno = con.insert(inserir)
        """        
        
        return msg_erro         

    def action_atualiza_clientes(self):
        # atualiza data nascimento
        #dt = datetime.today() - relativedelta(years=18) # quem é menor de 18 anos
        cliente = self.env['res.partner']
        mes = datetime.today().month()
        dia = datetime.today().day()
        #db = con.Conexao('192.168.0.50', 'C:\\home\\bd\\db_geral.fdb')
        msg_erro = ''
        msg_sis = 'Integrando Socios para o Clube <br>'
        hj = datetime.now()
        hj = hj - timedelta(days=250) # AQUI ESTOU PEGANDO A DATA DE HOJE MENOS 5 DIAS 
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        # inativos ('write_date', '>=', hj)
        """
            SOCIOS INATIVADOS
        """
        con = Conexao()
        """
        cli_ids = cliente.search([
            ('write_date', '>=', hj),
            ('customer','=', True), 
            ('active','=',False)])
        for partner_id in cli_ids:
            if not partner_id.chave_acesso:
                continue
            #print ('Socio/Depende : %s' %(partner_id.name))
            sqlc = 'select id, idDevice, inativo, name from \
                Users where idDevice = %s \
                and deleted = 0'  %(partner_id.chave_acesso)
            cli_fb = con.query(sqlc)
            for cli in cli_fb:
                # inativando cadastro
                altera = 'UPDATE Users SET inativo = 1 \
                     WHERE id = %s;' %(cli.id)
                retorno = con.insert(altera)
                if retorno:
                    msg_erro += 'ERRO : %s<br>' %(retorno)
        """
        #cli_ids = cliente.search([
        #    ('id', '=', 5031),

        # ARRUMAR MENORES
        dt = datetime.today() - relativedelta(years=18) # quem é menor de 18 anos
        #    if partner_id.data_nascimento > dt.date():      
        cli_ids = cliente.search([('data_nascimento', '>', dt.date()),
            ('customer','=', True),
            ('chave_acesso','!=', False),
            ])
        for partner_id in cli_ids:
            #if partner_id.chave_acesso == '117766':       
            #    import pudb;pu.db 
            sqlc = 'select u.id, u.idDevice, u.blackList, u.name, c.NumberStr from \
                Users u left outer join Cards c on c.idUser = u.id where idDevice = %s \
                and deleted = 0'  %(partner_id.chave_acesso)    
            cli_fb = con.query(sqlc)
            for cli in cli_fb:
                maior_18 = '3'
                altera = 'update useraccessrules set idAccessRule = %s \
                    where idUser = %s' %(maior_18, str(cli[0]))
                retorno = con.insert(altera)                
      
        cli_ids = cliente.search([('data_nascimento', '>', dt.date()),
            ('customer','=', True),
            ('chave_acesso','!=', False),
            ])
        for partner_id in cli_ids:
            #if partner_id.chave_acesso == '117766':       
            #    import pudb;pu.db
            sqlc = 'select u.id, u.idDevice, u.blackList, u.name, c.NumberStr from \
                Users u left outer join Cards c on c.idUser = u.id where idDevice = %s \
                and deleted = 0'  %(partner_id.chave_acesso)    
            cli_fb = con.query(sqlc)
            for cli in cli_fb:
                maior_18 = '1003'
                alteraGr = 'update usergroups set idGroup = %s \
                    where idUser = %s' %(maior_18, str(cli[0]))
                retorno = con.insert(alteraGr)               
                
            
        """
            SOCIOS ATIVOS
        """
        
        cli_ids = cliente.search([('write_date', '>=', hj),
            ('customer','=', True),
            ('chave_acesso','!=', False),
            ])
        for partner_id in cli_ids:
            #if partner_id.chave_acesso == '117772':        
            #    import pudb;pu.db
            #if partner_id.id == 3729:
            #    import pudb;pu.db
            nome = partner_id.name.strip()
            nome = nome.replace("'"," ")
            nome = unidecode(nome[:100])
            inadimplente = 0
            if partner_id.inadimplente:
                inadimplente = 1
            if partner_id.parent_id:
                if partner_id.parent_id.inadimplente:
                    inadimplente = 1
            if not partner_id.chave_acesso:
                continue
            sqlc = 'select u.id, u.idDevice, u.blackList, u.name, c.NumberStr from \
                Users u left outer join Cards c on c.idUser = u.id where idDevice = %s \
                and deleted = 0'  %(partner_id.chave_acesso)    
            cli_fb = con.query(sqlc)
            for cli in cli_fb:
                if cli[4] != partner_id.cartao:
                    # ve se precisa incluir o cartao
                    self.insere_cartao(partner_id.chave_acesso, partner_id.cartao)
                """
                 ALTERANDO/INCLUINDO
                """ 
                msg_erro = self.altera_socio(partner_id, nome)
                if not partner_id.image:
                    continue
                path_foto = '/media/win/fotos/%s.jpg' %(nome)
                with open(path_foto, 'wb') as f:
                    f.write(base64.decodebytes(partner_id.image))
                f.close()                
                if cli[2] == inadimplente  and cli[3] == nome:
                    continue
                    
            if not len(cli_fb):
                msg_erro = self.insere_novo_socio(partner_id, nome)
                if not partner_id.image:
                    continue
                path_foto = '/media/win/fotos/%s.jpg' %(nome)
                with open(path_foto, 'wb') as f:
                    f.write(base64.decodebytes(partner_id.image))
                f.close()
                """
                sqlf = 'SELECT \"Codigo\" FROM FOTOS WHERE \"Codigo\" = \'%s\'' %(partner_id.chave_acesso)
                foto = db.query(sqlf)
                if foto and len(foto[0]):    
                    delete = "DELETE FROM FOTOS WHERE \"Codigo\" = " + str(foto[0][0])
                    db.cursor.execute(delete)
                    db.connection.commit()
                
                with open('/home/odoo/foto.jpg', mode='rb') as f:
                    db.cursor.execute("insert into FOTOS values (?, ?)", (int(cod), f,))
                f.close()
                if retorno:
                    msg_erro += 'MSG RETORNO INSERT FOTO : %s<br>' %(retorno)
                """
        msg_sis += 'Integracao Finalizada.<br>'
        if msg_erro:
            msg_sis += msg_erro
        return  msg_sis
