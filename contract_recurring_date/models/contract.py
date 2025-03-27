# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta


class ContractRecurrencyMixin(models.AbstractModel):
    _inherit = "contract.recurrency.mixin"

    # funcao original troca a dia da proxima fatura para o mesmo dia que esta na data inicio
    @api.model
    def get_next_period_date_end(
        self,
        next_period_date_start,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
        next_invoice_date=False,
        recurring_invoicing_type=False,
        recurring_invoicing_offset=False,
    ):
        next_period_date_end = (
            self.contract_id.recurring_next_date
                - relativedelta(days=recurring_invoicing_offset)
                + self.get_relative_delta(recurring_rule_type, recurring_interval)
                - relativedelta(days=1)
            )
        return next_period_date_end

"""
class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.depends(
        "contract_line_ids.recurring_next_date",
        "contract_line_ids.is_canceled",
    )
    def _compute_recurring_next_date(self):
        # Compute the recurring_next_date on the contract based on the one
        # defined on line level.
        #for contract in self:
            #recurring_next_date = contract.contract_line_ids.filtered(
            #    lambda l: (
            #        l.recurring_next_date
            #        and not l.is_canceled
            #        and (not l.display_type or l.is_recurring_note)
            #    )
            #).mapped("recurring_next_date")
            # Take the earliest or set it as False if contract is stopped
            # (no recurring_next_date).
            #contract.recurring_next_date = (
            #    min(recurring_next_date) if recurring_next_date else False
            #)
        for rec in self:
            recurring_next_date = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
            )
            rec.recurring_next_date = recurring_next_date
"""