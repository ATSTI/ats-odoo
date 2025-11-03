
from odoo import models, _, api, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def _prepare_tax_ibscbs(self):
        vals = {}     
        if not self.fiscal_document_line_id or not self.product_id:
            return vals
        # if not self.move_id.fiscal_document_id.nfe_environment == '2':
        #     return
        # line = self.fiscal_document_line_id
        ibs_cbs = False
        import pudb;pu.db
        if self.fiscal_operation_id:
            for fiscal_line in self.fiscal_operation_line_id.tax_definition_ids:
                if fiscal_line.tax_domain == 'ibscbs':
                    # self._remove_all_fiscal_tax_ids()
                    ibs_cbs = True
                #     line.ibscbs_cst_id = fiscal_line.tax_id.cst_out_id.id
                #     line.ibscbs_cst_code = fiscal_line.tax_id.cst_out_id.code
                #     line.ibscbs_tax_id = fiscal_line.tax_id.id
                #     line.ibs_reduction = fiscal_line.tax_id.percent_reduction
                # elif fiscal_line.tax_domain == 'ibsuf':
                #     line.ibsuf_tax_id = fiscal_line.tax_id.id
                #     line.ibsuf_aliquota = fiscal_line.tax_id.percent_amount                    
                # elif fiscal_line.tax_domain == 'ibsmun':
                #     line.ibsmun_tax_id = fiscal_line.tax_id.id
                #     line.ibsmun_aliquota = fiscal_line.tax_id.percent_amount
                # elif fiscal_line.tax_domain == 'cbs':
                #     line.cbs_tax_id = fiscal_line.tax_id.id
                #     line.cbs_aliquota = fiscal_line.tax_id.percent_amount
                #     line.cbs_reduction = fiscal_line.tax_id.percent_reduction
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
                # self._remove_all_fiscal_tax_ids()
        return vals

        # # import pudb;pu.db
        # base_cbs = self.amount_untaxed - (self.amount_untaxed * (line.cbs_reduction/100) if line.cbs_reduction else 0.00)
        # base_ibs = self.amount_untaxed - (self.amount_untaxed * (line.ibs_reduction/100) if line.ibs_reduction else 0.00)
        # self.ibscbs_base = base_ibs
        # self.cbs_value = base_cbs * ((line.cbs_aliquota/100) if line.cbs_aliquota else 0.00)
        # self.ibsuf_value = base_ibs * ((line.ibsuf_aliquota/100) if line.ibsuf_aliquota else 0.00)
        # self.ibsmun_value = base_ibs * ((line.ibsmun_aliquota/100) if line.ibsmun_aliquota else 0.00)

    @api.onchange("cbs_tax_id", "price_unit", "quantity", "fiscal_price", "fiscal_quantity", "amount_untaxed")
    def _onchange_cbs_tax_id(self):        
        """Calcula ibs/cbs tax id"""
        values = self._prepare_tax_ibscbs()
        self._onchange_fiscal_operation_id()
        self._onchange_fiscal_operation_line_id()
        
        self._onchange_fiscal_taxes()
        if len(values):
            self.update(values)

        # for line in self:
        #     # import pudb;pu.db
            
        #     line.cbs_value = line.amount_untaxed * (line.cbs_tax_id.percent_amount/100) if line.cbs_tax_id and line.amount_untaxed else 0.00

    # @api.onchange(
    #     "amount_currency",
    #     "currency_id",
    #     "debit",
    #     "credit",
    #     "tax_ids",
    #     "fiscal_tax_ids",
    #     "account_id",
    #     "price_unit",
    #     "quantity",
    #     "fiscal_quantity",
    #     "fiscal_price",
    # )
    # def _onchange_mark_recompute_taxes(self):
    #     """Recompute the dynamic onchange based on taxes.
    #     If the edited line is a tax line, don't recompute anything as the
    #     user must be able to set a custom value.
    #     """
        
    #     return super()._onchange_mark_recompute_taxes()    