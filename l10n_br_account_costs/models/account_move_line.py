from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ...l10n_br_fiscal.constants.fiscal import (
    CFOP_DESTINATION_EXPORT,
    FISCAL_IN,
    FISCAL_OUT,
)


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = [_name, "l10n_br_fiscal.document.line.mixin.methods"]
    _inherits = {"l10n_br_fiscal.document.line": "fiscal_document_line_id"}

    # @api.model
    # def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
    #     # import pudb;pu.db
    #     res = super()._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
    #     # import pudb;pu.db
    #     line_discount_price_unit = price_unit * (1 - (discount / 100.0))
    #     subtotal = quantity * line_discount_price_unit
    #     # subtotal = subtotal + self.freight_value + self.insurance_value + self.other_value
    #     res['price_total'] = res['price_subtotal'] = subtotal
    #     if currency:
    #         res = {k: currency.round(v) for k, v in res.items()}
    #     return res

    # estava calculando o preco sem os impostos qdo marcado como dedutivel
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.
        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        result = super()._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit
        # Compute 'price_total'.
        if taxes:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            operation_line=self.env.context.get("fiscal_operation_line_id")
            cfop=self.cfop_id
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(
                line_discount_price_unit,
                currency=currency,
                quantity=quantity,
                product=product,
                partner=partner,
                is_refund=move_type in ('out_refund', 'in_refund'),
                handle_price_include=True, # FIXME
                fiscal_taxes=self.env.context.get("fiscal_tax_ids"),
                operation_line=operation_line,
                cfop=cfop,
                ncm=self.env.context.get("ncm_id"),
                nbs=self.env.context.get("nbs_id"),
                nbm=self.env.context.get("nbm_id"),
                cest=self.env.context.get("cest_id"),
                discount_value=self.env.context.get("discount_value"),
                insurance_value=self.env.context.get("insurance_value"),
                other_value=self.env.context.get("other_value"),
                freight_value=self.env.context.get("freight_value"),
                fiscal_price=self.env.context.get("fiscal_price"),
                fiscal_quantity=self.env.context.get("fiscal_quantity"),
                uot=self.env.context.get("uot_id"),
                icmssn_range=self.env.context.get("icmssn_range"),
                icms_origin=self.env.context.get("icms_origin"))

            result['price_subtotal'] = taxes_res['total_excluded']
            result['price_total'] = taxes_res['total_included']

            fol = self.env.context.get("fiscal_operation_line_id")
            # import pudb;pu.db
            if operation_line:
                fiscal_operation_type = operation_line.fiscal_operation_type or FISCAL_OUT
                if (
                    cfop
                    and cfop.destination != CFOP_DESTINATION_EXPORT
                    and fiscal_operation_type != FISCAL_IN
                ):
                    if fol and not fol.fiscal_operation_id.deductible_taxes:
                        result['price_subtotal'] = taxes_res['total_excluded'] - taxes_res['amount_tax_included']
                        result['price_total'] = taxes_res['total_included'] - taxes_res['amount_tax_included']

        return result

    # @api.onchange("fiscal_tax_ids")
    # def _onchange_fiscal_tax_ids(self):
    #     """Ao alterar o campo fiscal_tax_ids que contém os impostos fiscais,
    #     são atualizados os impostos contábeis relacionados"""
    #     result = super()._onchange_fiscal_tax_ids()
    #     user_type = "sale"

    #     # Atualiza os impostos contábeis relacionados aos impostos fiscais
    #     if self.move_id.move_type in ("in_invoice", "in_refund"):
    #         user_type = "purchase"
    #     self.tax_ids |= self.fiscal_tax_ids.account_taxes(user_type=user_type)

    #     # Caso a operação fiscal esteja definida para usar o impostos
    #     # dedutíveis os impostos contáveis deduvíveis são adicionados na linha
    #     # da movimentação/fatura.

    #     import pudb;pu.db
    #     # na nota importacao, ignorar deductible
    #     deductible=True
    #     fiscal_operation_type = self.fiscal_operation_line_id.fiscal_operation_type or FISCAL_OUT
    #     if (
    #         self.cfop_id
    #         and self.cfop_id.destination == CFOP_DESTINATION_EXPORT
    #         and fiscal_operation_type == FISCAL_IN
    #     ):
    #         deductible=False

    #     if self.fiscal_operation_id and self.fiscal_operation_id.deductible_taxes:
    #         self.tax_ids |= self.fiscal_tax_ids.account_taxes(
    #             user_type=user_type,
    #             deductible=deductible
    #         )

    #     return result