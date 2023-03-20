# -*- coding: utf-8 -*-

import fdb
import odoorpc
import fiscal
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
from unidecode import unidecode
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

# CONEXAO ATS-ADMIN
con = fdb.connect(dsn='192.168.0.108:/home/bd/sge_fritisco.fdb', user='sysdba', password='masterkey',charset='UTF8')
#con = fdb.connect(dsn='192.168.6.251/3050:/home/sisadmin/bd/sge_felicita.fdb', user='sysdba', password='masterkey',charset='UTF8')
# Abre conexao com o banco da Sao Pedro Treino:
cur = con.cursor()

#CONEXAO ODOO
# Prepare the connection to the server
#odoo = odoorpc.ODOO('192.168.6.100', port=8069)
odoo = odoorpc.ODOO('192.168.0.104', port=8069)
# Login
#odoo.login('19_conquista', 'ats@atsti.com.br', 'a2t00s7')
odoo.login('novo', 'manmdsantos@yahoo.com.br', 'a2t00s7')


odoo_user = odoo.env['res.users']

sqlu = 'SELECT NOMEUSUARIO FROM USUARIO WHERE CODUSUARIO > 0'
cur.execute(sqlu)
cadastra = 0
#import pudb;pu.db
for row in cur.fetchall():
    usuario = unidecode(str(row[0]))
    user_id = odoo_user.search([('name', '=', usuario)])
    if user_id:
        continue
    import pudb;pu.db
    cadastra += 1
    print ('Usuario : %s.' % (usuario))
    odoo_user.create({'name': usuario, 'login': usuario})


odoo_cliente = odoo.env['res.partner']
odoo_city = odoo.env['res.state.city']
#odoo_fiscal = odoo.env['br_base.tools.fiscal']

#city = odoo.env['l10n_br_base.city']

hj = datetime.now()
hj = hj - timedelta(days=5)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')