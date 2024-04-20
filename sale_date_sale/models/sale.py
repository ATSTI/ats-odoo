# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    date_sale = fields.Date(string="Data da venda")