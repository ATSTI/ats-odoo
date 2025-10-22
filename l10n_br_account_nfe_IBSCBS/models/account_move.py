
from odoo import models, _, api, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def _prepare_tax_ibscbs(self):
        if not self.fiscal_document_line_id:
            return
        if not self.move_id.fiscal_document_id.nfe_environment == '2':
            return
        line = self.fiscal_document_line_id
        ibs_cbs = False
        if self.fiscal_operation_id:
            for fiscal_line in self.fiscal_operation_line_id.tax_definition_ids:
                if fiscal_line.tax_domain == 'ibscbs':
                    ibs_cbs = True
                    line.ibscbs_cst_id = fiscal_line.tax_id.cst_out_id.id
                    line.ibscbs_cst_code = fiscal_line.tax_id.cst_out_id.code
                    line.ibscbs_tax_id = fiscal_line.tax_id.id
                elif fiscal_line.tax_domain == 'ibsuf':
                    line.ibsuf_tax_id = fiscal_line.tax_id.id
                elif fiscal_line.tax_domain == 'ibsmun':
                    line.ibsmun_tax_id = fiscal_line.tax_id.id
                elif fiscal_line.tax_domain == 'cbs':
                    line.cbs_tax_id = fiscal_line.tax_id.id
        if not ibs_cbs:
            if self.move_id.company_id.ibscbs_cst_id:
                line.ibscbs_cst_id = self.move_id.company_id.ibscbs_cst_id.id
                line.ibscbs_cst_code = self.move_id.company_id.ibscbs_cst_id.code
                line.ibsuf_tax_id = self.move_id.company_id.ibsuf_tax_id.id
                line.ibsmun_tax_id = self.move_id.company_id.ibsmun_tax_id.id
                line.cbs_tax_id = self.move_id.company_id.cbs_tax_id.id
        line.cbs_value = line.amount_untaxed * (line.cbs_tax_id.percent_amount/100) if line.cbs_tax_id and line.amount_untaxed else 0.00

    @api.onchange(
        "amount_currency",
        "currency_id",
        "debit",
        "credit",
        "tax_ids",
        "fiscal_tax_ids",
        "account_id",
        "price_unit",
        "quantity",
        "fiscal_quantity",
        "fiscal_price",
    )
    def _onchange_mark_recompute_taxes(self):
        """Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the
        user must be able to set a custom value.
        """
        self._prepare_tax_ibscbs()
        return super()._onchange_mark_recompute_taxes()    