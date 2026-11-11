from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveProductPrint(models.TransientModel):
    _name = "account.move.product.print"
    _description = "Impressão de Produtos da Fatura"

    move_id = fields.Many2one("account.move", required=True)
    move_line_ids = fields.Many2many(
        "account.move.line",
        string="Produtos",
        domain="[('move_id', '=', move_id), ('product_id', '!=', False)]",
    )

    def action_print(self):
        self.ensure_one()
        if not self.move_line_ids:
            raise UserError("Selecione ao menos um produto para imprimir o cupom.")
        return self.env.ref(
            "field_service_custom.report_selected_products"
        ).report_action(self, data={
            "move_id": self.move_id.id,
            "move_line_ids": self.move_line_ids.ids,
        })