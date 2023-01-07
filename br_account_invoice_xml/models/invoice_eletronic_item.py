# -*- coding: utf-8 -*-
# © 2018 Carlos R. Silveira, Atsti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models



class InvoiceEletronicItem(models.Model):
    _inherit = "invoice.eletronic.item"

    importado = fields.Boolean(string=u'Importado', default=False)
    #num_item = fields.Integer(
    #    string=u"Sequêncial Item", default=1, readonly=True, states=STATE)
