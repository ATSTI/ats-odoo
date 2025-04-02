# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta


class ContractLine(models.Model):
    _inherit = "contract.line"

<<<<<<< HEAD
    def _update_recurring_next_date(self):
        # isso modifica a recurring_next_date de forma q nao queremos
        pass

class ContractContract(models.Model):
    _inherit = "contract.contract"
    
    @api.depends(
        "contract_line_ids.recurring_next_date",
        "contract_line_ids.is_canceled",
    )
    def _compute_recurring_next_date(self):
        # Compute the recurring_next_date on the contract based on the one
        # defined on line level.
        for contract in self:
            contract.recurring_next_date = contract.recurring_next_date + relativedelta(months=1)

    def _prepare_invoice(self, date_invoice, journal=None):
        self.ensure_one()
        invoice_vals, move_form = super()._prepare_invoice(date_invoice, journal)
        invoice_vals.update({"move_tag_ids": self.tag_ids})
        return invoice_vals, move_form
