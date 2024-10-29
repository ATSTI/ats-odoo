# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [
        _name,
        "l10n_br_fiscal.document.move.mixin",
    ]
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    _order = "date DESC, name DESC"

    def _recompute_fiscal_operation_id(self, move):
        move._compute_amount()
        for line in move.invoice_line_ids:
            line.fiscal_operation_id = move.fiscal_operation_id
            line._onchange_fiscal_operation_id()
            # line._onchange_price_subtotal()       
        move._recompute_dynamic_lines(recompute_all_taxes=True)
        move._recompute_payment_terms_lines()

    def action_copiar_fatura(self):
        name_move = f"Fatura-{self.name}"
        move_created = self.env['account.move'].search([
            ('ref', '=', name_move)
        ])
        if move_created:
            raise ValidationError(
                _("Documento NFe já criado para esta fatura.")
            )
        vals = {}
        vals["partner_id"] = self.partner_id.id
        document = self.env['l10n_br_fiscal.document.type'].search([
            ("code", "=", 55)
        ],limit=1)
        vals["document_type_id"] = document.id
        vals["document_serie_id"] = document.document_serie_ids[0].id
        operacao = self.env['l10n_br_fiscal.operation'].search([
            ("name", "ilike", "venda")
        ],limit=1)
        vals["fiscal_operation_id"] = operacao.id
        vals["payment_mode_id"] = self.payment_mode_id.id
        vals["invoice_date_due"] = self.invoice_date_due
        vals["ref"] = name_move
        # TODO fazer a busca do diario a utilizar
        vals["journal_id"] = 3
        vals["document_date"] = self.document_date
        vals["invoice_user_id"] = self.invoice_user_id.id
        vals["currency_id"] = self.currency_id.id
        vals["issuer"] = "company"
        # vals["move_type"] = "out_invoice"
        vals["move_type"] = "entry"
        tem_produtos = False
        for line in self.invoice_line_ids:
            if line.product_id.type in ("product", "consu"):
                tem_produtos = True
        if not tem_produtos:
            raise ValidationError(
                _("Fatura somente com serviços, sem produto para gerar NFe.")
            )
        move = super(AccountMove, self.with_context(create_from_move=True)).create(
            vals
        )

        for line in self.invoice_line_ids:
            if line.product_id.type == "service":
                continue
            item = {}

            fiscal_operation_line_id = operacao.line_definition(
                company=move.company_id,
                partner=line.partner_id,
                product=line.product_id,
            )
            discount = line.discount_value
            if line.discount and not line.discount_value:
                discount = (line.quantity * line.price_unit * line.discount) / 100
            item["partner_id"] = line.partner_id.id
            item["product_id"] = line.product_id.id
            item["account_id"] = line.account_id.id
            item["quantity"] = line.quantity
            item["discount"] = line.discount
            item["discount_value"] = discount
            item["fiscal_quantity"] = line.quantity
            item["product_uom_id"] = line.product_uom_id.id
            item["uot_id"] = line.product_uom_id.id
            item["price_unit"] = line.price_unit
            item["fiscal_price"] = line.price_unit
            item["price_subtotal"] = line.price_subtotal
            item["name"] = line.name
            item["tax_icms_or_issqn"] = line.product_id.tax_icms_or_issqn
            item["fiscal_type"] = line.product_id.fiscal_type
            item["fiscal_operation_id"] = operacao.id
            item["fiscal_operation_line_id"] = fiscal_operation_line_id.id
            item["uom_id"] = line.product_id.uom_id.id
            item["ncm_id"] = line.product_id.ncm_id.id
            item["icms_origin"] = line.product_id.icms_origin
            item["fiscal_genre_id"] = line.product_id.fiscal_genre_id.id
            move.write({'invoice_line_ids': [(0, 0, item)]})
        for line in move.invoice_line_ids:
            line._onchange_product_id_fiscal()
            line._onchange_fiscal_operation_id()
        self._recompute_fiscal_operation_id(move)        
        if move:
            return {
                'res_id': move.id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }
        return move
