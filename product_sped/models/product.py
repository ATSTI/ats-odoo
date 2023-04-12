# -*- coding: utf-8 -*-
# © 2017  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from .cst import TIPO_ITEM


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tipo_item = fields.Selection(TIPO_ITEM, 'Tipo Item')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
