# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class RepairOrder(models.Model):
    _inherit = 'repair.order'
    
    material_request_line_ids = fields.One2many(
        'itens.requisitados',
        'repair_id',
        string='Materiais'
    )

    material_devolution_line_ids = fields.One2many(
        'itens.devolvidos',
        'repair_id',
        string='Materiais'
    )

class ItensRequisitados(models.Model):
    _name = 'itens.requisitados'
    _description = 'Linha de Requisição (livre)'

    repair_id = fields.Many2one(
        'repair.order',
        ondelete='cascade'
    )

    item = fields.Char(string='Item', required=True)
    quantidade = fields.Float(string='Quantidade', default=1)
    obs = fields.Char(string='Observação')
    who_req = fields.Char(string='Requirente')
    date_req = fields.Date(string='Data de Requisição')

class ItensDevolvidos(models.Model):
    _name = 'itens.devolvidos'
    _description = 'Linha de Devolução (livre)'

    repair_id = fields.Many2one(
        'repair.order',
        ondelete='cascade'
    )

    item = fields.Char(string='Item', required=True)
    quantidade = fields.Float(string='Quantidade', default=1)
    obs = fields.Char(string='Observação')
    who_devol = fields.Char(string='Restintuinte')
    date_devol = fields.Date(string='Data de Devolução')
