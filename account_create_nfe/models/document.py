from odoo import _, api, fields, models
from odoo.exceptions import UserError

class DocumentNfe(models.Model):
    _inherit = "l10n_br_fiscal.document"

    @api.depends("move_ids", "move_ids.financial_move_line_ids")
    def _compute_nfe40_dup(self):        
        for record in self.filtered(lambda x: x._need_compute_nfe40_dup()):
            if (record.move_ids.ref and record.move_ids.invoice_origin and 
                record.move_ids.ref == "NFe-" + record.move_ids.invoice_origin):
                dups_vals = []
                #            "nfe40_vDup": mov.debit,
                for count, mov in enumerate(record.move_ids.financial_move_line_ids, 1):
                    dups_vals.append(
                        {
                            "nfe40_nDup": str(count).zfill(3),
                            "nfe40_dVenc": mov.date_maturity,
                            "nfe40_vDup": record.amount_total,
                        }
                    )
                record.nfe40_dup = [(2, dup, 0) for dup in record.nfe40_dup.ids]
                record.nfe40_dup = [(0, 0, dup) for dup in dups_vals]
            else:
                super()._compute_nfe40_dup()
