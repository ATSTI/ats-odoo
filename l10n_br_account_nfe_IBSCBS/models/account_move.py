
from odoo import models, _, api, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def _prepare_tax_ibscbs(self):
        vals = {}     
        if not self.fiscal_document_line_id or not self.product_id:
            return vals
        ibs_cbs = False
        if self.fiscal_operation_id:
            for fiscal_line in self.fiscal_operation_line_id.tax_definition_ids:
                if fiscal_line.tax_domain == 'ibscbs':
                    ibs_cbs = True
        if not ibs_cbs:
            if self.move_id.company_id.ibscbs_cst_id:
                vals = {
                    "ibscbs_cst_id": self.move_id.company_id.ibscbs_cst_id.id,
                    "ibscbs_cst_code": self.move_id.company_id.ibscbs_cst_id.code,
                    "ibs_reduction": self.move_id.company_id.ibsuf_tax_id.percent_reduction,
                    "ibsuf_tax_id": self.move_id.company_id.ibsuf_tax_id.id,
                    "ibsuf_aliquota": self.move_id.company_id.ibsuf_tax_id.percent_amount,
                    "ibsmun_tax_id": self.move_id.company_id.ibsmun_tax_id.id,
                    "ibsmun_aliquota": self.move_id.company_id.ibsmun_tax_id.percent_amount,
                    "cbs_tax_id": self.move_id.company_id.cbs_tax_id.id,
                    "cbs_reduction": self.move_id.company_id.cbs_tax_id.percent_reduction,
                    "cbs_aliquota": self.move_id.company_id.cbs_tax_id.percent_amount,
                }
        return vals

    @api.onchange("cbs_tax_id", "price_unit", "quantity", "fiscal_price", "fiscal_quantity", "amount_untaxed")
    def _onchange_cbs_tax_id(self):        
        """Calcula ibs/cbs tax id"""
        values = self._prepare_tax_ibscbs()
        self._onchange_fiscal_operation_id()
        self._onchange_fiscal_operation_line_id()
        
        self._onchange_fiscal_taxes()
        if len(values):
            self.update(values)
