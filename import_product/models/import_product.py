# -*- coding: utf-8 -*-

from odoo import api, fields, models
import base64
import csv
from datetime import datetime, date
import tempfile
import time
import xlrd
import re


class ImportProduct(models.Model):
    _name = 'import.product'
    
    name = fields.Char('Descrição', size=256, required=True, default='/')
    input_file = fields.Binary('Arquivo', required=False)
    user_id = fields.Many2one('res.users', string='Inserido por', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    header =  fields.Boolean('Header')
    state = fields.Selection([
        ('open', 'Novo'),
        ('done', 'Importado'),
        ('cancel', 'Cancelado'),
        ], string='Situação', readonly=True, copy=False, index=True, track_visibility='onchange', default='open')

    @api.multi
    def set_done(self):
        return self.write({'stage': 'done'})
        
    @api.multi
    def set_open(self):
        return self.write({'stage': 'open'})

    @api.multi
    def set_cancelled(self):
        return self.write({'stage': 'cancelled'})


    @api.multi
    def import_to_db(self):
        prod_obj = self.env['product.product']
        #uom_obj = self.env['product.uom']
        prodtmpl_obj = self.env['product.template']
        for chain in self:
            #file_path = tempfile.gettempdir()+'/file.xls'
            #file_path = '/home/odoo/planilhacarlos.xls'
            file_path = '/home/odoo/mairibel_p.xls'

            #data = chain.input_file
            #f = open(file_path,'wb')
            #f.write(data.decode('base64'))
            #f.close()
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)

            conta_registros = 0
            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                if rownum > 0 and rownum < 300:

                    vals = {}

                    # Mairibel
                    if rowValues[1]:
                        cod = rowValues[1]
                        vals['default_code'] = str(int(cod))
                    descricao = ''
                    if rowValues[2]:
                        descricao = rowValues[2]
                        vals['name'] = rowValues[2]
                    p_id = prod_obj.search([('name', '=', descricao)])
                    if p_id:
                        continue
                    if descricao:
                        print ('Produto: %s' %(descricao))                        
                                                                    
                    if rowValues[6]:
                       vals['list_price'] = float(rowValues[6])
                       vals['standard_price'] = float(rowValues[6]) * 0.5  
                    vals['type'] = 'product'
                    vals['uom_id'] = 1
                    #vals['uom_po_id'] = 1
                    
                    if rowValues[18]:
                        vals['length'] = rowValues[23]
                        vals['weight'] = rowValues[18]
                        vals['height'] = rowValues[22]
                        vals['width'] = rowValues[21]
                    
                    ncm = ''
                    if rowValues[4]:
                        ncm = str(int(rowValues[4])).zfill(8)
                        #ncm = '%s.%s.%s' % (ncm[:4], ncm[4:6], ncm[6:8])
                        pf_ids = self.env['product.fiscal.classification'].search([('code', '=', ncm)])
                        if pf_ids:
                            vals['fiscal_classification_id'] = pf_ids.id
                    if rowValues[39]:
                        vals['cest'] = str(int(rowValues[39]))
                    
                    p_id =  prod_obj.create(vals)
                    #except:    
                    #    print ('ERRO Produto: s')
                    conta_registros += 1
             #print ('TOTAL DE REGISTROS INCLUIDOS : %s') %(str(conta_registros))
             #if conta_registros in (50,150,200,250,300,350,400,450,500,600,700,800,900,1000,1100,1200,1300,1400,1500):
             #    cr.commit()

        return self.write({'state':'done'})
