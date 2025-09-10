# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models


class Operation(models.Model):
    """
      Altero o metodo line_definition para considerar o NCM na escolha da linha
        de operacao fiscal
    """
    _inherit = "l10n_br_fiscal.operation"

    def line_definition(self, company, partner, product):
        self.ensure_one()
        if not company:
            company = self.env.company
        lines = self.line_ids.search(self._line_domain(company, partner, product))
        if product:
            for line in lines:
                tax_ids = line._get_cfop(company, partner).tax_definition_ids
                if not tax_ids:
                    tax_ids = line.tax_definition_ids
                for tx in tax_ids:
                    if not tx.ncms:
                        continue
                    delimiter=","
                    field_codes = tx.ncms.replace(".", "")
                    list_codes = field_codes.split(delimiter)
                    
                    if [tax for tax in list_codes if tax == product.ncm_id.code_unmasked]:
                        return line
                    
        return self._select_best_line(lines)