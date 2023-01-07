# -*- coding: utf-8 -*-

from odoo import api, fields, models
import base64
import csv
from datetime import datetime, date
import tempfile
import time
import xlrd
import re
from odoo.exceptions import UserError


class ImportNfePlanilha(models.Model):
    _name = 'import.nfe.planilha'
    
    name = fields.Char('Descrição', default='/')

    @api.multi
    def import_to_db(self):
        import pudb;pu.db
        file_path = '/home/odoo/file.xls'
        #file_path = tempfile.gettempdir()+'/file.xls'
        #data = base64.decodebytes(self.input_file)
        #f = open(file_path,'wb')
        #f.write(data)
        #f.close()
        book = xlrd.open_workbook(file_path)
        first_sheet = book.sheet_by_index(0)
        
        conta_registros = 0
        
        active_ids = self.env.context.get('active_ids', [])
        for rownum in range(first_sheet.nrows):                                                                                                       
            rowValues = first_sheet.row_values(rownum)
            if rownum > 1 and rowValues[1]:
                vals = {}
                nfe_obj = self.env['invoice.eletronic']
                if rowValues[1]:
                    nota = str(int(rowValues[1]))
                    nfe_id = nfe_obj.search([('numero', '=', nota)])
                    if nfe_id:
                        chave = rowValues[2]
                        nfe_id.write({'chave_nfe': chave, 
                             'codigo_retorno': '100',
                             'mensagem_retorno': 'Autorizado o uso da NF-e',
                             'state': 'done',
                         })
        
