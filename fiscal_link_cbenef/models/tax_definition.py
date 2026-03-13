# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, _
from odoo.exceptions import ValidationError

class TaxDefinition(models.Model):
    _inherit = "l10n_br_fiscal.tax.definition"

    def _get_complete_name(self):
        return f"{self.tax_id.name} - {self.cst_code} - {self.code} - {self.description}"

    @api.constrains("company_id")
    def _check_company_id(self):
        for record in self:
            if record.company_id:
                domain = [
                    ("id", "!=", record.id),
                    ("company_id", "=", record.company_id.id),
                    ("tax_group_id", "=", record.tax_group_id.id),
                    ("tax_id", "=", record.tax_id.id),
                    ("is_benefit", "=", record.is_benefit),
                    ("code", "=", record.code),
                ]

                if record.env["l10n_br_fiscal.tax.definition"].search_count(domain):
                    raise ValidationError(
                        _(
                            "Tax Definition already exists "
                            "for this Company and Tax Group !"
                        )
                    )