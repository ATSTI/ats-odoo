from odoo import models, fields
from .cst import ORIGEM_PROD


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type_bkp = fields.Selection(
        [('service', u'Serviço'), ('product', 'Produto')], 'Tipo Fiscal',
        )
    fiscal_type_bkp = fields.Selection(
        selection=[
            ("00", "Mercadoria para Revenda"),
            ("01", "Matéria-prima"),
            ("02", "Embalagem"),
            ("03", "Produto em Processo"),
            ("04", "Produto Acabado"),
            ("05", "Subproduto"),
            ("06", "Produto Intermediário"),
            ("07", "Material de Uso e Consumo"),
            ("08", "Ativo Imobilizado"),
            ("09", "Serviços"),
            ("10", "Outros insumos"),
            ("99", "Outras"),
        ],
    )
    origin_bkp = fields.Selection(ORIGEM_PROD, 'Origem', default='0')
    ncm = fields.Char(string="NCM", size=14)
    code_servico = fields.Char(u'Código Serviço', size=16)
