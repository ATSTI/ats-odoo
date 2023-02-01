# Copyright (C) 2009  Renato Lima - Akretion, Gabriel C. Stabel
# Copyright (C) 2012  Raphaël Valyi - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice(self):

        # frete, outros e seguro nao entrando na fatura

        self.ensure_one()
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update(
            {
                "fiscal_operation_id": self.fiscal_operation_id.id,
                "document_type_id": self.company_id.document_type_id.id,
                "amount_freight_value": self.amount_freight_value,
                "amount_other_value": self.amount_other_value,
                "amount_insurance_value": self.amount_insurance_value,
            }
        )
        return invoice_vals
