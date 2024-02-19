# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models


class Operation(models.Model):
    _inherit = "l10n_br_fiscal.operation"

    def _line_domain(self, company, partner, product):
        domain = super()._line_domain(company, partner, product)
        fiscal_type = product.fiscal_type
        icms_origin = product.icms_origin
        if product:
            # import pudb;pu.db
            if not product.icms_origin or not product.fiscal_type:
                prd_id = "product.template,{}".format(product.product_tmpl_id.id)
                prd = self.env["ir.property"].sudo().search([
                    ("type", "=", "selection"),
                    ("res_id", "=", prd_id),
                ])
                for p in prd:
                    if p.name == "fiscal_type" and not product.fiscal_type:
                        fiscal_type = p.value_text
                    if p.name == "icms_origin" and not product.icms_origin:
                        icms_origin = p.value_text

                domain = [
                    ("fiscal_operation_id", "=", self.id),
                    ("fiscal_operation_type", "=", self.fiscal_operation_type),
                    ("state", "=", "approved"),
                ]

                domain += [
                    "|",
                    ("date_start", "=", False),
                    ("date_start", "<=", fields.Datetime.now()),
                    "|",
                    ("date_end", "=", False),
                    ("date_end", ">=", fields.Datetime.now()),
                ]

                domain += [
                    "|",
                    ("company_tax_framework", "=", company.tax_framework),
                    ("company_tax_framework", "=", False),
                ]

                domain += [
                    "|",
                    ("ind_ie_dest", "=", partner.ind_ie_dest),
                    ("ind_ie_dest", "=", False),
                ]

                domain += [
                    "|",
                    ("partner_tax_framework", "=", partner.tax_framework),
                    ("partner_tax_framework", "=", False),
                ]

                domain += [
                    "|",
                    ("product_type", "=", fiscal_type),
                    ("product_type", "=", False),
                ]

                domain += [
                    "|",
                    ("tax_icms_or_issqn", "=", product.tax_icms_or_issqn),
                    ("tax_icms_or_issqn", "=", False),
                ]

                domain += [
                    "|",
                    ("icms_origin", "=", icms_origin),
                    ("icms_origin", "=", False),
                ]

        return domain
