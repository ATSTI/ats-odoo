from odoo import models, fields


class PosProductReportWizard(models.TransientModel):
    _name = 'pos.product.report.wizard'
    _description = 'Relatório POS por Produto'

    product_id = fields.Many2one(
        'product.product',
        string='Produto',
        required=True
    )

    def action_print_report(self):
        return self.env.ref(
            'pos_produtos_report.report_pos_product_sales'
        ).report_action(self)
