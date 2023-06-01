# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from . import atscon as con
from unidecode import unidecode
from io import BytesIO
from io import StringIO
from PIL import Image
import fdb as Database
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
     
    # 17/12/2020
    @api.depends("data_nascimento")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.data_nascimento:
                age = relativedelta(fields.Date.today(), record.data_nascimento).years
            record.age = age

    #30/09/20 
    @api.multi
    def write(self, vals):
        #import pudb;pu.db
        #partner_id = self
        # atualiza BD
        res = super(ResPartner, self).write(vals)                      
        db = con.Conexao('192.168.0.50', 'C:\\home\\bd\\db_geral.fdb')
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
                #import pudb;pu.db
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
                            #import pudb;pu.db
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
            #    import pudb;pu.db
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
        db = con.Conexao('192.168.0.50', 'C:\\home\\bd\\db_geral.fdb')
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
            ], order='partner_id')
        # altero todos no BD para Inadimplente = F
        altera =  'UPDATE SOCIOS SET \"Inadimplente\" = \'F\''
        retorno = db.insert(altera)
        # procurando quem esta no Odoo Inadimplente = False
        prt_ids = self.env['res.partner'].search([
            ('customer', '=', True),
            ('inadimplente', '=', True),
        ])
        for prt in prt_ids:
            #if prt.id == 949:
            #import pudb;pu.db
            if not prt.parent_id:
                cnt_ids = conta.search([('reconciled', '=', False), 
                    ('date_maturity', '<', hj),
                    ('user_type_id.type', '=', 'receivable'),
                    ('partner_id', '=', prt.id),
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
                altera =  'UPDATE SOCIOS SET \"Inadimplente\" = \'T\' \
                    WHERE \"Via\" = %s' %(sc.chave_acesso)
                retorno = db.insert(altera)
                parent_ids = self.env['res.partner'].search([
                    ('parent_id', '=', sc.id),
                    ('customer', '=', True),
                ])
                for parent in parent_ids:
                    parent.sudo().write({'inadimplente': True})               
                    altera =  'UPDATE SOCIOS SET \"Inadimplente\" = \'T\' \
                        WHERE \"Via\" = %s' %(parent.chave_acesso)
                    retorno = db.insert(altera)
                socio = conta.partner_id.id

    def action_atualiza_clientes(self):  
        db = con.Conexao('192.168.0.50', 'C:\\home\\bd\\db_geral.fdb')
        msg_erro = ''
        msg_sis = 'Integrando Socios para o Clube <br>'
        hj = datetime.now()
        hj = hj - timedelta(days=3) # AQUI ESTOU PEGANDO A DATA DE HOJE MENOS 5 DIAS 
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        cliente = self.env['res.partner']
        
        # inativos ('write_date', '>=', hj)
        cli_ids = cliente.search([
            ('write_date', '>=', hj),
            ('customer','=', True), 
            ('active','=',False)])
        for partner_id in cli_ids:
            if not partner_id.chave_acesso:
                continue
            #print ('Socio/Depende : %s' %(partner_id.name))
            nome = partner_id.name.strip()
            nome = nome.replace("'"," ")
            nome = unidecode(nome)            
            sqlc = 'select \"Via\", \"Data Desligamento\" from SOCIOS where \"Via\" = %s' %(partner_id.chave_acesso)
            cli_fb = db.query(sqlc)
            for cli in cli_fb:
                altera =  'UPDATE SOCIOS SET \"Data Desligamento\" = \'%s\' \
                         WHERE "Via\" = %s' %(cli[1], str(partner_id.chave_acesso))
                retorno = db.insert(altera )
                if retorno:
                    #import pudb;pu.db
                    msg_erro += 'ERRO : %s<br>' %(retorno)
        #cli_ids = cliente.search([
        #    ('id', '=', 2516),
        cli_ids = cliente.search([('write_date', '>=', hj),
            ('customer','=', True),
            ('chave_acesso','!=', False),
            ])
        for partner_id in cli_ids:
            if not partner_id.chave_acesso:
                continue
            #print ('Socio/Depende : %s' %(partner_id.name))
            sqlc = 'select  \"Codigo\" , \"Nome\" , \"Titulo\" , \"Categoria\" , \"Via\" \
                            ,"Dependente\" , \"Inadimplente\" , \"Parentesco\" , \"Codigo_Titular\" , \"Data de Nascimento\" \
            from SOCIOS where \"Via\" = %s' %(partner_id.chave_acesso)
            
            nome = partner_id.name.strip()
            nome = nome.replace("'"," ")
            nome = unidecode(nome)
            #if partner_id.id == 4773:
            #    import pudb;pu.db
            
            inadimplente = 'F'
            if partner_id.inadimplente:
                inadimplente = 'T'
 
            dependente = 'F'
            if partner_id.dependente:
                dependente = 'T' 

            parentesco = 'F'
            if partner_id.parentesco:
                parentesco = 'T'
            data_nasc = 'Null'
            if partner_id.data_nascimento:
                data_nasc = '\'' + str(partner_id.data_nascimento) + '\''
            #if partner_id.chave_acesso == '117522':
            #import pudb;pu.db
            cli_fb = db.query(sqlc)
            if len(cli_fb):
                cli = cli_fb[0]
                e_depend = 'Null'
                if partner_id.parent_id:
                    e_depend = partner_id.parent_id.chave_acesso
                    sqlc = 'select  \"Codigo\" \
                          from SOCIOS where \"Via\" = %s' %(e_depend)
                    depend = db.query(sqlc)
                    if depend and not len(depend):
                        continue
                    if depend and len(depend):
                        e_depend = str(depend[0][0])
                    else:
                        continue
                altera =  'UPDATE SOCIOS SET \"Nome\" = \'%s\' , \"Titulo\" = \'%s\', \"Categoria\" = \'%s\', \"Via\" = \'%s\', \
                           \"Dependente\" = \'%s\' , \"Inadimplente\" = \'%s\', \"Parentesco\" = \'%s\', \"Codigo_Titular\" = %s , \
                           \"Data de Nascimento\" = %s \
                         WHERE \"Via\" = %s' %(nome,partner_id.vat,partner_id.categoria,partner_id.chave_acesso,
                               dependente,inadimplente,parentesco,e_depend,data_nasc,partner_id.chave_acesso)
                retorno = db.insert(altera )
                if not partner_id.image:
                    continue
                sqlf = 'SELECT \"Codigo\" FROM FOTOS WHERE \"Codigo\" = %s' %(str(cli[0]))
                foto = db.query(sqlf)
                with open('/home/odoo/foto.jpg', 'wb') as f:
                    f.write(base64.decodebytes(partner_id.image))
                f.close()
                if foto and len(foto[0]):    
                    delete = "DELETE FROM FOTOS WHERE \"Codigo\" = " + str(foto[0][0])
                    db.cursor.execute(delete)
                    db.connection.commit()
                    #with open('/home/ubuntu/foto.jpg', mode='rb') as f:
                    #    update = "UPDATE FOTOS SET \"Foto\" = ? WHERE \"Codigo\" = " + str(foto[0][0])
                    #    db.cursor.execute(update, (f,))
                    #f.close()
                #else:
                with open('/home/odoo/foto.jpg', mode='rb') as f:
                    try:
                        db.cursor.execute("insert into FOTOS values (?, ?)", (str(cli[0]), f,))
                    except:
                        #import pudb;pu.db
                        msg_erro += 'ERRO : %s<br>' %(retorno)
                    db.connection.commit()
                f.close()
                retorno = ''                
                if retorno:
                    msg_erro += 'ERRO : %s<br>' %(retorno)
            if not len(cli_fb):
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
                
                inadimplente = 'F'
                if partner_id.inadimplente:
                    inadimplente = 'T' 
 
                dependente = 'F'
                if partner_id.dependente:
                    dependente = 'T' 

                parentesco = 'F'
                if partner_id.parentesco:
                    parentesco = 'T'                    
                #import pudb;pu.db    
                e_depend = 'Null'
                if partner_id.parent_id:
                    if not partner_id.parent_id.chave_acesso:
                        continue
                    e_depend = partner_id.parent_id.chave_acesso
                    sqlc = 'select  \"Codigo\" \
                          from SOCIOS where \"Via\" = %s' %(e_depend)
                    depend = db.query(sqlc)
                    if depend and not len(depend):
                        continue
                    if depend and len(depend):
                        e_depend = str(depend[0][0])
                    else:
                        continue
                
                cod = partner_id.chave_acesso
                categ = '1'
                if partner_id.categoria:
                    categ = partner_id.categoria
                insere = 'insert into SOCIOS (\"Codigo\" , \"Nome\" , \"Titulo\" , \"Categoria\" , \"Via\" \
                            ,\"Dependente\" , \"Inadimplente\" , \"Parentesco\" , \"Codigo_Titular\",\"Data de Nascimento\" ) \
                            values (%s,\'%s\',\'%s\',\'%s\',%s,\'%s\',\'%s\',\'%s\',%s ,%s )' \
                            %(int(cod), partner_id.name, partner_id.vat, categ, partner_id.chave_acesso,
                            dependente, inadimplente, parentesco , e_depend, data_nasc)  
                try:
                    retorno = db.insert(insere)
                except:
                    msg_erro += 'ERRO INSERINDO SOCIO NOVO : %s<br>' %(retorno)
                if retorno:
                    #import pudb;pu.db
                    msg_erro += 'MSG : %s<br>' %(retorno)

                if not partner_id.image:
                    continue
                
                with open('/home/odoo/foto.jpg', 'wb') as f:
                    f.write(base64.decodebytes(partner_id.image))
                f.close()

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
        msg_sis += 'Integracao Finalizada.<br>'
        return  msg_sis + '<br>' + msg_erro
