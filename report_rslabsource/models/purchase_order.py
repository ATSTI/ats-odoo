from odoo import models, fields, api
from datetime import timedelta
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    moeda_cotacao = fields.Selection([
        ('USD', 'Dólar'),
        ('BRL', 'Real'),
    ], string='Moeda do pedido de compra', default='USD')

    sale_order_id = fields.Many2one('sale.order', string='Pedido de Venda de Origem')
    numero_orcamento = fields.Char(string='Nº do Orçamento',related='sale_order_id.name', store=True)
    numero_pedido_venda = fields.Char(string='Nº do Pedido de Venda',related='sale_order_id.name', store=True)
    validity_date = fields.Date(
        string='Validade do Pedido de Compra',
        compute='_compute_validity_date',
        store=True,
    )

    @api.depends('date_order')
    def _compute_validity_date(self):
        for order in self:
            if order.date_order:
                order.validity_date = order.date_order + timedelta(days=30)
            else:
                order.validity_date = False