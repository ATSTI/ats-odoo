from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    numero_orcamento = fields.Char(
        string='Nº do Orçamento',
        copy=False,
        readonly=True,
    )

    purchase_order_id = fields.Many2one('purchase.order', string='Pedido de Compra de Origem')

    numero_pedido_compra = fields.Char(
        string='Nº do Pedido de Compra',
        related='purchase_order_id.name',
        store=True,
    )

    moeda_cotacao = fields.Selection([
        ('USD', 'Dólar'),
        ('BRL', 'Real'),
    ], string='Moeda da cotação', default='USD')

    def action_confirm(self):
        res = super().action_confirm()

        for order in self:
            if not order.numero_orcamento:
                order.numero_orcamento = order.name

        return res