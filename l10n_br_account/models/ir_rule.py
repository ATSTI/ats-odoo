from odoo import api, models

class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    def _compute_domain(self, model_name, mode="read"):
        # calculado só pra não quebrar cache do método pai
        super()._compute_domain(model_name, mode=mode)

        # apenas substitui quando account.move e não sudo
        if model_name == "account.move" and not self.env.su:
            return ['|', ('fiscal_document_id', '=', False), ('fiscal_document_id', '!=', False)]
        if model_name == "account.move.line" and not self.env.su:
            return ['|', ('fiscal_document_line_id', '=', False), ('fiscal_document_line_id', '!=', False)]

        return super()._compute_domain(model_name, mode=mode)