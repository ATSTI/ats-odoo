# -*- coding: utf-8 -*-
###################################################################################
#
#    ATS TI Soluções.
#
###################################################################################

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    cfop_code = fields.Char(string='CFOP', related='cfop_id.code', readonly=True)