# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"


    partner_responsability_id = fields.Many2one(
            comodel_name="res.partner", string="Responsavel faturamento"
        )

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super()._prepare_invoice(
            date_invoice, journal=journal
        )
        if self.partner_responsability_id != self.partner_id:
            invoice_vals["partner_id"] = self.partner_responsability_id.id
        return invoice_vals, move_form
