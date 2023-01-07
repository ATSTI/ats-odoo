# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.product'

    complemento = fields.Char(string="Tamanho/Peso/Medida")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    complemento = fields.Char(related='product_variant_ids.complemento', readonly=False)
    
