# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import requests


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_id_meli = fields.Char('Orders do pedido Mercado Livre')
