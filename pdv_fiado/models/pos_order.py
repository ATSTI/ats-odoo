# # -*- coding: utf-8 -*-
# from odoo import models, fields, api


# class PosOrder(models.Model):
#     _inherit = 'pos.order'

#     extra_note = fields.Char(string='CPF / Obs. adicional', default='')

#     @api.model
#     def _order_fields(self, ui_order):
#         import pudb;pudb.set_trace()
#         fields = super()._order_fields(ui_order)
#         fields['extra_note'] = ui_order.get('extra_note', '')
#         return fields

#     def _prepare_invoice_vals(self):
#         vals = super()._prepare_invoice_vals()
#         import pudb;pudb.set_trace()
#         if self.extra_note:
#             partner = self.env['account.move']._get_or_create_cpf_partner(
#                 self.extra_note
#             )
#             if partner:
#                 vals['partner_id'] = partner.id
#         return vals