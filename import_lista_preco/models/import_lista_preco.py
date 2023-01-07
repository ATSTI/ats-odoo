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


class ImportListaPreco(models.Model):
    _name = 'import.lista.preco'
    
    name = fields.Char('Descrição', default='/')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True)
    input_file = fields.Binary('Arquivo')
    input_file_name = fields.Char(
        string=u"Arquivo")
    user_id = fields.Many2one('res.users', string='Inserido por', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('open', 'Novo'),
        ('done', 'Importado'),
        ('cancel', 'Cancelado'),
        ], string='Situação', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    #@api.multi
    #def set_done(self):
    #    return self.write({'stage': 'done'})
        
    #@api.multi
    #def set_open(self):
    #    return self.write({'stage': 'open'})

    #@api.multi
    #def set_cancelled(self):
    #    return self.write({'stage': 'cancelled'})

    @api.model                                                                                                                                            
    def create(self, vals):
        active_ids = self.env.context.get('active_ids', [])
        lista = self.env['product.pricelist'].browse(active_ids)            
        vals['pricelist_id'] = lista.id                                                                                                                               
        if vals['name'] == '/':
            #import pudb;pu.db
            today = datetime.today()
            vals['name'] = '%s - (%s-%s-%s)' %(lista.name, 
            str(today.day).zfill(2), 
            str(today.month).zfill(2), str(today.year))
            vals['state'] = 'open'
        return super(ImportListaPreco, self).create(vals)
 
    @api.multi
    def import_to_db(self):
        if self.input_file:
            file_path = tempfile.gettempdir()+'/file.xls'
            #file_path = '/home/odoo/planilhacarlos.xls'
            #file_path = '/home/carlos/Downloads/produtos.xls'
            #file_path = '/opt/odoo/produtos.xls'
            #import pudb;pu.db
            data = base64.decodebytes(self.input_file)
            f = open(file_path,'wb')
            f.write(data)
            f.close()
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)

            conta_registros = 0
            
            active_ids = self.env.context.get('active_ids', [])
            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                if rownum > 0 and rowValues[1]:
                    vals = {}
                    prod_obj = self.env['product.template']
                    if rowValues[1]:
                        p_id = prod_obj.search([('default_code', '=', str(int(rowValues[1])))])
                        if p_id:
                            lista_id = self.env['product.pricelist.item'].search([
                                ('product_tmpl_id', '=', p_id.id),
                                ('pricelist_id','=',active_ids[0])])
                                
                            if lista_id:
                                lista_id.write({'fixed_price': rowValues[2]})
            self.write({'state': 'done'})
        else:
            raise UserError('Informe a Planilha a ser importada.')
        
class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    def action_import_lista(self):
        dummy, act_id = self.env['ir.model.data'].get_object_reference(                                                                               
            'import_lista_preco', 'import_lista_action')                                                                                  
        vals = self.env['ir.actions.act_window'].browse(act_id).read()[0]                                                                             
        return vals
        """  return {                                                                                                                                      
            'name': 'Importar Planilha de Preço',                                                                                                 
            'type': 'ir.actions.act_window',                                                                                                      
            'view_mode': 'form',                                                                                                                  
            'res_model': 'import.lista.preco',                                                                                              
            'target': 'new',                                                                                                                      
            'res_id': self.id,                                                                                                                                                                        
           }"""
