# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _recompute_fiscal_operation_id(self, move):
        move._compute_amount()
        # for line in move.invoice_line_ids:
        #     line.fiscal_operation_id = move.fiscal_operation_id
        #     line._onchange_fiscal_operation_id()
        #    # line._onchange_price_subtotal()       
        move._recompute_dynamic_lines(recompute_all_taxes=True)
        move._recompute_payment_terms_lines()

    def action_copiar_fatura(self):
        if not self.payment_mode_id:
            raise ValidationError(
               _("Fatura sem forma de pagamento, campo obrigatório")
            )
        name_move = f"NFse-{self.name}"
        move_created = self.env["account.move"].search([
            ("ref", "=", name_move),
            ("invoice_origin", "=", self.name),
            ("state", "in", ("draft", "posted")),
        ])
        if move_created:
            raise ValidationError(
                _("Documento NFse já criado para esta fatura.")
            )
        vals = {}
        vals["partner_id"] = self.partner_id.id
        document = self.env['l10n_br_fiscal.document.type'].search([
            ("code", "=", "SE")
        ],limit=1)
        journal = self.env['account.journal'].search([
            ("type", "=", "general")
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
        vals["invoice_origin"] = self.name
        # TODO fazer a busca do diario a utilizar
        vals["journal_id"] = journal.id
        vals["document_date"] = self.document_date
        vals["invoice_user_id"] = self.invoice_user_id.id
        vals["currency_id"] = self.currency_id.id
        vals["issuer"] = "company"
        # vals["move_type"] = "out_invoice"
        vals["move_type"] = "entry"
        tem_servico = False
        total_servico = 0.0
        for line in self.invoice_line_ids:
            if line.product_id.type in "service":
                tem_servico = True
                total_servico += line.price_subtotal
        vals["amount_total_signed"] = total_servico
        if not tem_servico:
            self.write({"ref": "Produto"})
            title = _('Fatura/NFse'),
            message = _("Fatura somente com Produtos, sem serviços para gerar NFse"),       
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'sticky': False,
                 }
            }
        move = super(AccountMove, self.with_context(create_from_move=True)).create(
            vals
        )
        for line in self.invoice_line_ids:
            if line.product_id.type != "service":
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
            # move.write({'invoice_line_ids': [(0, 0, item)]})
            item["move_id"] = move.id
            move_item = self.env["account.move.line"].create(item)
            move_item.fiscal_operation_id = move.fiscal_operation_id
            move_item._onchange_product_id_fiscal()
            move_item._onchange_fiscal_operation_id()
            move_item.price_unit = line.price_unit
            move_item.fiscal_price = line.price_unit
        # for line in move.invoice_line_ids:
        #     line.fiscal_operation_id = move.fiscal_operation_id
        #     line._onchange_product_id_fiscal()
        #     line._onchange_fiscal_operation_id()
        #     line.price_unit = line.price_unit
        #     line.fiscal_price = line.price_unit
        self._recompute_fiscal_operation_id(move)
        self.message_post(
            body=_(
                "<a href='#' data-oe-model='%s' data-oe-id='%s'>NFse criada diário: %s</a>"
            ) % (move._name, move.id, journal.name)
        )
        # self.write({"ref": "NFse"})
        move.message_post(
            body=_(
                "<a href='#' data-oe-model='%s' data-oe-id='%s'>NFse da Fatura %s</a>"
            ) % (self._name, self.id, self.name)
        )        
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
