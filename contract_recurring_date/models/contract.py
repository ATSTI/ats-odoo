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
