from odoo import models, api
from datetime import datetime, timedelta


class PosProductSalesReport(models.AbstractModel):
    _name = 'report.pos_produtos_report.pos_product_sales_template'

    @api.model
    def _get_report_values(self, docids, data=None):

        wizard = self.env['pos.product.report.wizard'].browse(docids)

        date_from = datetime.now() - timedelta(days=30)

        lines = self.env['pos.order.line'].search([
            ('product_id', '=', wizard.product_id.id),
            ('order_id.date_order', '>=', date_from),
            ('order_id.state', 'in', ['paid', 'done', 'invoiced'])
        ])

        total_qty = sum(lines.mapped('qty'))
        total_value = sum(lines.mapped('price_subtotal_incl'))

        return {
        'doc': wizard,
        'lines': lines,
        'total_qty': total_qty,
        'total_value': total_value,
        'currency': self.env.company.currency_id,
    }

