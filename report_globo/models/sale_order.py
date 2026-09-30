from odoo import models, fields, api
from num2words import num2words

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def float_para_extenso(self, numero):
            if not numero:
                return ''
    
            # Separa parte inteira e decimal com 2 casas
            inteiro, decimal = f"{numero:.2f}".split('.')
            
            extenso_inteiro = num2words(int(inteiro), lang='pt_BR')
            
            if int(decimal) == 0:
                return extenso_inteiro
                
            extenso_decimal = num2words(int(decimal), lang='pt_BR')
            if len(decimal) == 2 and decimal.startswith('0'):
                extenso_decimal = f"zero {extenso_decimal}"
                
            return f"{extenso_inteiro} vírgula {extenso_decimal}"