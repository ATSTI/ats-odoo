# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date


class ContractContract(models.Model):
    _inherit = 'contract.contract'

       
    amount_total = fields.Float(string='Valor Total', compute='_compute_amount_total', store=True)
    
    @api.depends('contract_line_ids.price_subtotal')
    def _compute_amount_total(self):
        for contract in self:
            contract.amount_total = sum(line.price_subtotal for line in contract.contract_line_ids)   
