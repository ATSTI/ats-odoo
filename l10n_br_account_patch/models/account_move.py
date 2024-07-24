# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    # removendo o document_type_id qdo o diario for cash ou bank
    # sem isso nao permite baixar a fatura da erro:
    # "To Generate EDoc Key, you need to fill th..."

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        fiscal_document_line_ids = {}
        for idx1, move_val in enumerate(vals_list):
            if "invoice_line_ids" in move_val:
                fiscal_document_line_ids[idx1] = {}
                for idx2, line_val in enumerate(move_val["invoice_line_ids"]):
                    if (
                        line_val[0] == 0
                        and line_val[1] == 0
                        and isinstance(line_val[2], dict)
                    ):
                        fiscal_document_line_ids[idx1][idx2] = line_val[2].get(
                            "fiscal_document_line_id", False
                        )

        for vals in vals_list:
            journal = vals.get("journal_id")
            if self.env["account.journal"].browse([journal]).type in ['cash','bank']:
                vals["document_type_id"] = False
        new_vals_list = super(
            AccountMove, self.with_context(lines_compute_amounts=True)
        )._move_autocomplete_invoice_lines_create(vals_list)
        for vals in new_vals_list:
            if not vals.get("document_type_id"):
                vals["fiscal_document_id"] = False

        for idx1, move_val in enumerate(new_vals_list):
            if "line_ids" in move_val:
                if fiscal_document_line_ids.get(idx1):
                    idx2 = 0
                    for line_val in move_val["line_ids"]:
                        if (
                            line_val[0] == 0
                            and line_val[1] == 0
                            and isinstance(line_val[2], dict)
                        ):
                            line_val[2][
                                "fiscal_document_line_id"
                            ] = fiscal_document_line_ids[idx1].get(idx2)
                            idx2 += 1

        return new_vals_list

    # def write(self, values):
    #     # No PDV esta dando erro: To Generate EDoc Key ...
    #     if "line_ids" in values and "POS/" in values["line_ids"][0][2]["name"]:
    #         values["document_type_id"] = False
    #     result = super().write(values)
    #     return result