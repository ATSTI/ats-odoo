# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from erpbrasil.base.fiscal import cnpj_cpf

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class Partner(models.Model):

    _inherit = 'res.partner'

    # se preencher sem pontos esta rotina esta falhando
    @api.constrains("vat", "l10n_br_ie_code")
    def _check_cnpj_l10n_br_ie_code(self):
        for record in self:
            domain = []

            if not record.vat:
                return

            if self.env.context.get(
                "disable_allow_cnpj_multi_ie"
            ) or self.env.context.get("allow_vat_duplicate"):
                return

            allow_cnpj_multi_ie = (
                record.env["ir.config_parameter"]
                .sudo()
                .get_param("l10n_br_base.allow_cnpj_multi_ie", default=True)
            )

            if record.parent_id:
                domain += [
                    ("id", "not in", record.parent_id.ids),
                    ("parent_id", "not in", record.parent_id.ids),
                ]

            if record.vat:
                domain += [
                    "|",
                    ("vat", "=", record.vat),
                    ("cnpj_cpf_stripped", "=", record.cnpj_cpf_stripped),
                    ("id", "!=", record.id),
                    ("parent_id", "!=", record.id),
                ]
                # return

            matches = record.env["res.partner"].search(domain)
            if matches:
                if cnpj_cpf.validar_cnpj(record.vat):
                    if allow_cnpj_multi_ie == "True":
                        for partner in record.env["res.partner"].search(domain):
                            if (
                                partner.l10n_br_ie_code == record.l10n_br_ie_code
                                and record.l10n_br_ie_code
                            ):
                                raise ValidationError(
                                    _(
                                        "Já existe um parceiro %(name)s "
                                        "(ID %(partner_id)s) com esta "
                                        "Inscrição Estadual %(incr_est)s!",
                                        name=partner.name,
                                        partner_id=partner.id,
                                        incr_est=partner.l10n_br_ie_code,
                                    )
                                )
                    else:
                        raise ValidationError(
                            _(
                                "Já existe um parceiro %(name)s "
                                "(ID %(partner_id)s) com este CNPJ %(vat)s!",
                                name=matches[0].name,
                                partner_id=matches[0].id,
                                vat=self.vat,
                            )
                        )
                elif not record.is_company:
                    raise ValidationError(
                        _(
                            "Já existe um parceiro %(name)s (ID %(partner_id)s) "
                            "com este CPF/RG! %(vat)s",
                            name=matches[0].name,
                            partner_id=matches[0].id,
                            vat=matches[0].vat,
                        )
                    )

    def write(self, vals_list):
        if not self.user_id and 'user_id' in vals_list:
            return super().write(vals_list)
        if 'user_id' in vals_list:
            if self.user_id != self.env.user and not self.env.user.has_group('sales_team.group_sale_manager'):
                raise UserError(_("Você não pode alterar o campo Vendedor do Contato se este não for seu, ou você não for Administrador de Vendas"))
        return super().write(vals_list)

