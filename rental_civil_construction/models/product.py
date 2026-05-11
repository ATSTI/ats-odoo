from odoo import models, fields, api
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_rental = fields.Boolean(string="É um produto de locação?", default=False)
    rental_price = fields.Float(string="Preço de Locação", digits='Product Price')
    rental_duration = fields.Integer(string="Duração da Locação (dias)")

    owner_value_type = fields.Selection([('percent', 'Percentagem'), ('amount', 'Valor')], string='Tipo de calculo',
        default='percent')
    owner_value_rate = fields.Float('Valor do Proprietário', digits=dp.get_precision('Account'))

    @api.constrains('rental_price', 'owner_value_rate')
    def _check_rental_price(self):
        if self.rental_price < 0:
            raise UserError('O preço de locação não pode ser negativo.')
        if self.owner_value_rate > self.rental_price:
            raise UserError('O valor do proprietário não pode ser maior que o preço de locação.')



   