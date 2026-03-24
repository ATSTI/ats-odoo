# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class TaxDefinition(models.Model):
    _inherit = "l10n_br_fiscal.tax.definition"

    # benefit_type = fields.Selection(
    #     selection=ICMS_TAX_BENEFIT_TYPE,
    #     states={"draft": [("readonly", False)]},
    # )
    benefit_type = fields.Selection(
        selection_add=[
            ("7", "7 - Não incidência"),
            ("9", "9 - Outros"),
        ],
    )

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

    # # adicionado aqui pra usar esta constants do icms, da oca nao permite codigo 7 e 9
    # @api.constrains("is_benefit", "code", "benefit_type", "state_from_id")
    # def _check_tax_benefit_code(self):
    #     for record in self:
    #         if record.is_benefit:
    #             if record.code:
    #                 if len(record.code) != 8:
    #                     raise ValidationError(
    #                         _("Tax benefit code must be 8 characters!")
    #                     )

    #                 if record.code[:2].upper() != record.state_from_id.code.upper():
    #                     raise ValidationError(
    #                         _("Tax benefit code must be start with state code!")
    #                     )
    #                 import pudb;pu.db
    #                 if record.code[3:4] != record.benefit_type:
    #                     raise ValidationError(
    #                         _(
    #                             "The tax benefit code must contain "
    #                             "the type of benefit!"
    #                         )
    #                     )
