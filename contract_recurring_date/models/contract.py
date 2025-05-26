# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta


class ContractLine(models.Model):
    _inherit = "contract.line"

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
            if contract.recurring_next_date:
                contract.recurring_next_date = contract.recurring_next_date + relativedelta(months=1)

    def _prepare_invoice(self, date_invoice, journal=None):
        self.ensure_one()
        invoice_vals, move_form = super()._prepare_invoice(date_invoice, journal)
        invoice_vals.update({"move_tag_ids": self.tag_ids})
        return invoice_vals, move_form

    def _get_lines_to_invoice(self, date_ref, resp=None):
        self.ensure_one()
        def can_be_invoiced(contract_line):
            return True
        #    return (
                #not contract_line.is_canceled
                #and contract_line.recurring_next_date
                #and contract_line.recurring_next_date <= date_ref
        #    )
        ctr_id = self
        if resp:
            ctr_id = self.contract_responsability(resp)
        lines2invoice = previous = self.env["contract.line"]
        current_section = current_note = False
        for ct in ctr_id:
            for line in ct.contract_line_ids:
                if line.display_type == "line_section":
                    current_section = line
                elif line.display_type == "line_note" and not line.is_recurring_note:
                    if line.note_invoicing_mode == "with_previous_line":
                        if previous in lines2invoice:
                            lines2invoice |= line
                        current_note = False
                    elif line.note_invoicing_mode == "with_next_line":
                        current_note = line
                elif line.is_recurring_note or not line.display_type:
                    if can_be_invoiced(line):
                        if current_section:
                            lines2invoice |= current_section
                            current_section = False
                        if current_note:
                            lines2invoice |= current_note
                        lines2invoice |= line
                        current_note = False
                previous = line
        return lines2invoice.sorted()
