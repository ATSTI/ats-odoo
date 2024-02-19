# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression
from dateutil.relativedelta import relativedelta


class ContractContract(models.Model):
    _inherit = "contract.contract"


    partner_responsability_id = fields.Many2one(
            comodel_name="res.partner", string="Responsavel faturamento"
        )

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super()._prepare_invoice(
            date_invoice, journal=journal
        )
        if self.partner_responsability_id and self.partner_responsability_id != self.partner_id:
            invoice_vals["partner_id"] = self.partner_responsability_id.id
        else:
            invoice_vals["partner_id"] = self.partner_id.id
        return invoice_vals, move_form
    
    def _recurring_create_invoice(self, date_ref=False):
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        moves = self.env["account.move"].create(invoices_values)
        self._add_contract_origin(moves)
        self._invoice_followers(moves)
        # mv = moves[-1]
        # self._compute_recurring_next_date()
        self._change_recurring_next_date()
        moves.action_post()
        return moves
    
    def contract_responsability(self, resp):
        create_type="invoice"
        date_ref = fields.Date.context_today(self)
        domain = self._get_contracts_to_invoice_domain(date_ref)
        domain = expression.AND(
            [
                domain,
                [
                    ("generation_type", "=", create_type),
                    ("partner_responsability_id", "=", resp.id), 
                ],
            ]
        )
        contracts = self.search(domain)
        companies = set(contracts.mapped("company_id"))
        # Invoice by companies, so assignation emails get correct context
        ctr_id = self
        for company in companies:
            ctr_id = contracts.filtered(
                lambda c: c.company_id == company
                and (not c.date_end or c.recurring_next_date <= c.date_end)
            ).with_company(company)
        return ctr_id

    def _get_lines_to_invoice(self, date_ref, resp=None):
        """
        This method fetches and returns the lines to invoice on the contract
        (self), based on the given date.
        :param date_ref: date used as reference date to find lines to invoice
        :return: contract lines (contract.line recordset)
        """
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
    
    def _change_recurring_next_date(self):
        # Compute the recurring_next_date on the contract based on the one
        # defined on line level.
        for contract in self:
            if contract.recurring_rule_type == 'monthly':
                contract.recurring_next_date = contract.recurring_next_date + relativedelta(months=1)
            # if contract.recurring_next_date.month < data_venc.month:
            # fatura = self._get_related_invoices()
            # for fat in fatura:
            #     venc = fat.invoice_date_due.month
                
            # recurring_next_date = contract.contract_line_ids.filtered(
            #     lambda l: (
            #         l.recurring_next_date
            #         and not l.is_canceled
            #         and (not l.display_type or l.is_recurring_note)
            #     )
            # ).mapped("recurring_next_date")
            # # Take the earliest or set it as False if contract is stopped
            # # (no recurring_next_date).
            # contract.recurring_next_date = (
            #     min(recurring_next_date) if recurring_next_date else False
            # )
    
    def _prepare_recurring_invoices_values(self, date_ref=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        ctr_ids = set()
        ctr_ids_resp = set()
        for ctr in self:
            if ctr.partner_responsability_id:
                ctr_ids_resp.add(ctr.partner_responsability_id.id)
            else:
                ctr_ids.add(ctr.partner_id.id)
        invoices_values = []
        ja_faturado = set()
        for contract in self:
            faturar = False
            if ctr_ids_resp and contract.partner_responsability_id and contract.partner_responsability_id.id in ctr_ids_resp:
                faturar = True
                prt_id = contract.partner_responsability_id.id
            elif ctr_ids and contract.partner_id.id in ctr_ids:
                faturar = True
                prt_id = contract.partner_id.id
            if not faturar:
                continue
            if ja_faturado and prt_id in ja_faturado:
                continue
            ja_faturado.add(prt_id)
            if not date_ref:
                date_ref = contract.recurring_next_date
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref, contract.partner_responsability_id)
            if not contract_lines:
                continue
            invoice_vals, move_form = contract._prepare_invoice(date_ref)
            invoice_vals["invoice_line_ids"] = []
            for line in contract_lines:
                invoice_line_vals = line._prepare_invoice_line(move_form=move_form)
                if invoice_line_vals:

                    # Allow extension modules to return an empty dictionary for
                    # nullifying line. We should then cleanup certain values.
                    invoice_line_vals["name"] = f"{invoice_line_vals['name']} ({line.contract_id.partner_id.name})"
                    del invoice_line_vals["company_id"]
                    del invoice_line_vals["company_currency_id"]
                    invoice_vals["invoice_line_ids"].append((0, 0, invoice_line_vals))
            invoices_values.append(invoice_vals)
            # Force the recomputation of journal items
            del invoice_vals["line_ids"]
            # if ctr_ids_resp:
            #     ctr_ids_r = self.contract_responsability(contract.partner_responsability_id)
            #     for ct in ctr_ids_r:
            #         for line in ct.contract_line_ids:
            #             line._update_recurring_next_date()
            #     else:
            #         contract_lines._update_recurring_next_date()
        return invoices_values
