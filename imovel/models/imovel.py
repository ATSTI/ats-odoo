# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api
import re


class OwnerLine(models.Model):
    _name = 'owner.line'
    _description = 'Proprietário Imovel'
    
    partner_id = fields.Many2one('res.partner', 'Proprietário')
    cota = fields.Percent(u'Percentual Propriedade', default=100)
    owner_id = fields.Many2one('imovel', string='Imovél', index=True, required=True, ondelete='cascade')
    percentual_aluguel = fields.Percent(u'Percentual a Receber', default=10)
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Dia Pagamento'
        )

class Imovel(models.Model):
    _name = 'imovel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Cadastro Imovel"
    _order = "name"

    name = fields.Char('Imovel')
    active = fields.Boolean(
        'Ativo', default=True,
        help="Se desmarcado, este item estara desativado.")
    city_id = fields.Many2one(
        'res.state.city', u'Cidade',
        domain="[('state_id','=',state_id)]")
    number = fields.Char(u'Numero', size=10)
    zip = fields.Char('CEP', size=9)
    # , required=True
    street = fields.Char('Logradouro', size=72)
    district = fields.Char('Bairro', size=40)
    complemento = fields.Char('Complemento', size=80)
    country_id = fields.Many2one('res.country', 'Pais', default=31)
    state_id = fields.Many2one(
        'res.country.state', 'Estado',
        domain="[('country_id','=',country_id)]", default=95)
    owner_ids = fields.One2many('owner.line', 'owner_id', string='Proprietarios')
    quartos = fields.Integer(u'Quartos')
    banheiros = fields.Integer(u'Banheiros')
    area = fields.Float(u'Area')
    valor_aluguel = fields.Float(u'Valor Aluguel')
    alugado = fields.Boolean(u'Alugado')
    codigo_energia = fields.Char('Cód. Energia')
    codigo_agua = fields.Char('Cód. Agua')
    matricula = fields.Char('Matricula')
    # image: all image fields are base64 encoded and PIL-supported
    image_variant = fields.Binary(
        "Imagem", attachment=True,
        help="Foto do imovel, limitado a 1024x1024px.")
    image_small = fields.Binary(
        "Imagem pequena", attachment=True)
    description = fields.Text(
        'Descrição', translate=True)

    
    @api.onchange('zip')
    def _onchange_zip(self):
        cep = re.sub('[^0-9]', '', self.zip or '')
        if len(cep) == 8:
            self.zip_search(cep)

    def zip_search(self, cep):
        self.zip = "%s-%s" % (cep[0:5], cep[5:8])
        res = self.env['br.zip'].search_by_zip(zip_code=self.zip)
        if res:
            self.update(res)

    @api.onchange('street', 'city_id', 'district')
    def _search_street(self):
        if self.street and self.city_id and not self.zip:
            res = self.env['br.zip'].search_by_address(
                country_id=self.city_id.state_id.country_id.id,
                state_id=self.city_id.state_id.id,
                city_id=self.city_id.id,
                street=self.street,
                obj=None,
                district=self.district,
                error=False
            )
            if res:
                self.update(res)

"""
    @api.model
    def create(self, vals):
        if not 'name' in vals:
            if 'street' in vals:
                vals['name'] = vals['street']
                vals['purchase_ok'] = False
                vals['sale_ok'] = False
                vals['type'] = 'service'
            if 'street' in vals and 'number' in vals:
                vals['name'] = '%s,%s' %(vals['street'],vals['number'])
                vals['purchase_ok'] = False
                vals['sale_ok'] = False
                vals['type'] = 'service'

        return super(ProductProduct, self).create(vals)
"""

"""
    @api.multi
    def write(self, values):
        if 'street' in values:
            values['name'] = values['street']
            values['purchase_ok'] = False
            values['sale_ok'] = False
            values['type'] = 'service'
        if 'street' in values and 'number' in values:
            values['name'] = '%s,%s' %(values['street'],values['number'])
            values['purchase_ok'] = False
            values['sale_ok'] = False
            values['type'] = 'service'             
            
        return super(ProductProduct, self).write(values)
"""

"""
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    city_id = fields.Many2one(related='product_variant_ids.city_id', readonly=False)
    number = fields.Char(related='product_variant_ids.number', readonly=False)
    zip = fields.Char(related='product_variant_ids.zip', readonly=False)
    street = fields.Char(related='product_variant_ids.street', readonly=False)
    district = fields.Char(related='product_variant_ids.district', readonly=False)
    state_id = fields.Many2one(related='product_variant_ids.state_id', readonly=False)
    country_id = fields.Many2one(related='product_variant_ids.country_id', readonly=False)
    owner_ids = fields.One2many(related='product_variant_ids.owner_ids', readonly=False)
    quartos = fields.Integer(related='product_variant_ids.quartos', readonly=False)
    banheiros = fields.Integer(related='product_variant_ids.banheiros', readonly=False)
    area = fields.Float(related='product_variant_ids.area', readonly=False)
    imovel_ok = fields.Boolean(related='product_variant_ids.imovel_ok', readonly=False)
    codigo_agua = fields.Char(related='product_variant_ids.codigo_agua', readonly=False)
    codigo_energia = fields.Char(related='product_variant_ids.codigo_energia', readonly=False)
    matricula = fields.Char(related='product_variant_ids.matricula', readonly=False)

"""
