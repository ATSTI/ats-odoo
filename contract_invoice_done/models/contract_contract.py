# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"


    # def _prepare_invoice(self, date_invoice, journal=None):
    #     self.ensure_one()
    #     invoice_vals, move_form = super()._prepare_invoice(date_invoice, journal)
    #     invoice_vals.update(self._prepare_br_fiscal_dict())
    #     return invoice_vals, move_form

    # def _prepare_recurring_invoices_values(self, date_ref=False):
    #     """
    #     This method builds the list of invoices values to create, based on
    #     the lines to invoice of the contracts in self.
    #     !!! The date of next invoice (recurring_next_date) is updated here !!!
    #     :return: list of dictionaries (invoices values)
    #     """
    #     invoices_values = []
    #     for contract in self:
    #         if not date_ref:
    #             date_ref = contract.recurring_next_date
    #         if not date_ref:
    #             # this use case is possible when recurring_create_invoice is
    #             # called for a finished contract
    #             continue
    #         contract_lines = contract._get_lines_to_invoice(date_ref)
    #         if not contract_lines:
    #             continue
    #         invoice_vals, move_form = contract._prepare_invoice(date_ref)
    #         invoice_vals["invoice_line_ids"] = []
    #         for line in contract_lines:
    #             invoice_line_vals = line._prepare_invoice_line(move_form=move_form)
    #             if invoice_line_vals:
    #                 # Allow extension modules to return an empty dictionary for
    #                 # nullifying line. We should then cleanup certain values.
    #                 del invoice_line_vals["company_id"]
    #                 del invoice_line_vals["company_currency_id"]
    #                 invoice_vals["invoice_line_ids"].append((0, 0, invoice_line_vals))
    #         invoices_values.append(invoice_vals)
    #         # Force the recomputation of journal items
    #         del invoice_vals["line_ids"]
    #         contract_lines._update_recurring_next_date()
    #     return invoices_values

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref)
        # import pudb;pu.db
        for move in moves:

            # TODO verificar se carregou os dados corretamente do produto (fiscal)
            # TODO Validar a Fatura
            # TODO enviar a NFSe
            # TODO enviar o Boleto


            x = move.name
            # move.fiscal_document_id._onchange_document_serie_id()
            # move.fiscal_document_id._onchange_company_id()
            # move._onchange_invoice_line_ids()

        return moves

    # def _prepare_recurring_invoices_values(self, date_ref=False):
    #     """
    #     Overwrite contract method to verify and create invoices according to
    #     the Fiscal Operation of each contract line
    #     :return: list of dictionaries (inv_ids)
    #     """
    #     super_inv_vals = super()._prepare_recurring_invoices_values(date_ref=date_ref)

    #     if not self.fiscal_operation_id:
    #         for inv_val in super_inv_vals:
    #             inv_val["document_type_id"] = False
    #         return super_inv_vals

    #     if not isinstance(super_inv_vals, list):
    #         super_inv_vals = [super_inv_vals]

    #     inv_vals = []
    #     document_type_list = []

    #     for invoice_val in super_inv_vals:

    #         # Identify how many Document Types exist
    #         for inv_line in invoice_val.get("invoice_line_ids"):
    #             if type(inv_line[2]) == list:
    #                 continue

    #             operation_line_id = self.env["l10n_br_fiscal.operation.line"].browse(
    #                 inv_line[2].get("fiscal_operation_line_id")
    #             )

    #             fiscal_document_type = operation_line_id.get_document_type(
    #                 self.company_id
    #             )

    #             if fiscal_document_type.id not in document_type_list:
    #                 document_type_list.append(fiscal_document_type.id)
    #                 inv_to_append = invoice_val.copy()
    #                 inv_to_append["invoice_line_ids"] = [inv_line]
    #                 inv_to_append["document_type_id"] = fiscal_document_type.id
    #                 inv_to_append["document_serie_id"] = (
    #                     self.env["l10n_br_fiscal.document.serie"]
    #                     .search(
    #                         [
    #                             (
    #                                 "document_type_id",
    #                                 "=",
    #                                 inv_to_append["document_type_id"],
    #                             ),
    #                             ("company_id", "=", self.company_id.id),
    #                         ],
    #                         limit=1,
    #                     )
    #                     .id
    #                 )
    #                 inv_vals.append(inv_to_append)
    #             else:
    #                 index = document_type_list.index(fiscal_document_type.id)
    #                 inv_vals[index]["invoice_line_ids"].append(inv_line)

    #     return inv_vals
