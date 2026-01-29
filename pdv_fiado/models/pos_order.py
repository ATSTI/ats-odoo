from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    pos_extra_note = fields.Char('Dados adicionais (POS)')

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res['pos_extra_note'] = ui_order.get('extra_note')
        return res
