# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import re


class OwnerLine(models.Model):
    _name = 'owner.line'
    _description = 'Proprietário Imovel'
    
    partner_id = fields.Many2one('res.partner', 'Proprietário')
    name = fields.Char(string='Nome', related='partner_id.name', readonly=True)
    cota = fields.Float(u'Percentual Propriedade', default=100)
    owner_id = fields.Many2one('imovel', string='Imovél', index=True, required=True, ondelete='cascade')
    percentual_aluguel = fields.Float(u'Percentual a Receber', default=10)
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Dia Pagamento'
        )

class Imovel(models.Model):
    _name = 'imovel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Cadastro Imovel"
    _order = "name"

    name = fields.Char('Imovel', required=True)
    code = fields.Char(
        string="Código",
        default="/",
        required=True,
    )
    active = fields.Boolean(
        'Ativo', default=True,
        help="Se desmarcado, este item estara desativado.")
    country_id = fields.Many2one('res.country', 'Pais', default=31)
    state_id = fields.Many2one(
        'res.country.state', 'Estado',
        domain="[('country_id','=',country_id)]", default=95)
    city_id = fields.Many2one(
        string="Cidade",
        comodel_name="res.city",
        domain="[('state_id', '=', state_id)]",
    )
    number = fields.Char(u'Numero')
    zip_code = fields.Char('CEP')
    # , required=True
    street_name = fields.Char('Logradouro')
    district = fields.Char('Bairro')
    zip_complement = fields.Char('Complemento')
    owner_ids = fields.One2many('owner.line', 'owner_id', string='Proprietarios')
    quartos = fields.Integer(u'Quartos')
    banheiros = fields.Integer(u'Banheiros')
    areat = fields.Float(u'Area do Terreno')
    areac = fields.Float(u'Area da Contrução')
    valor_aluguel = fields.Float(u'Valor Aluguel')
    valor_venda = fields.Float(u'Valor Venda')
    alugado = fields.Boolean(u'Alugado')
    venda = fields.Boolean(u'Venda')
    locacao = fields.Boolean(u'Locação')
    codigo_energia = fields.Char('Cód. Energia')
    codigo_agua = fields.Char('Cód. Agua')
    matricula = fields.Char('Matricula')
    product_id = fields.Many2one('product.product', 'Produto', readonly=True)
    # image: all image fields are base64 encoded and PIL-supported
    image_variant = fields.Binary(
        "Imagem", attachment=True,
        help="Foto do imovel, limitado a 1024x1024px.")
    image_small = fields.Binary(
        "Imagem pequena", attachment=True)
    description = fields.Text(
        'Descrição', translate=True)

    
    @api.onchange('zip_code')
    def _onchange_zip(self):
        cep = re.sub('[^0-9]', '', self.zip_code or '')
        if len(cep) == 8:
            self.zip_search(cep)

    def zip_search(self, cep):
        self.zip_code = "%s-%s" % (cep[0:5], cep[5:8])
        res = self.env['l10n_br.zip']._consultar_cep(self.zip_code)
        if res:
            self.update(res)

    # @api.onchange('street', 'city_id', 'district')
    # def _search_street(self):
    #     if self.street and self.city_id and not self.zip:
    #         res = self.env['l10n_br.zip'].search_by_address(
    #             country_id=self.city_id.state_id.country_id.id,
    #             state_id=self.city_id.state_id.id,
    #             city_id=self.city_id.id,
    #             street=self.street,
    #             obj=None,
    #             district=self.district,
    #             error=False
    #         )
    #         if res:
    #             self.update(res)


    @api.model
    def create(self, vals):
        if "code" not in vals or vals["code"] == "/":
            vals['code'] = self.env['ir.sequence'].next_by_code('imovel.code') or '/'
        res = super(Imovel,self).create(vals)
        values = {}
        values['name'] = vals['name']
        values['default_code'] = vals['code']
        values['purchase_ok'] = False
        values['sale_ok'] = True
        values['fiscal_type'] = '09'
        values['tax_icms_or_issqn'] = 'issqn'
        values['type'] = 'service'

        prod = self.env['product.product'].create(values)
        res.product_id = prod.id
        return res

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
