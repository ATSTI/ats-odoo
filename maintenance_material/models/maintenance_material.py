# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import _, api, fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    material_ids = fields.One2many(
        comodel_name="maintenance.cost",
        inverse_name="maintenance_id",
        string="Material Used",
    )
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)

    @api.depends('material_ids')
    def _compute_amount(self):
        for line in self.material_ids:
            totals = line.price_unit * line.product_qty
            line.update({
                'price_total': totals,
            })

class MaintenanceCost(models.Model):
    """Added Product and Quantity in the Task Material Used."""

    _name = "maintenance.cost"
    _description = "Maintenance Material Used"

    maintenance_id = fields.Many2one(
        comodel_name="maintenance.request", string="OM", ondelete="cascade", required=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True,
        tracking=True,
    )
    currency_id = fields.Many2one(related='maintenance_id.currency_id', store=True, string='Currency', readonly=True)
    name = fields.Char(string="Descrição")
    product_uom = fields.Many2one('uom.uom', string='Unidade')
    product_qty = fields.Float(string='Quantidade', digits='Product Unit of Measure', required=True,
                               store=True, readonly=False)
    price_unit = fields.Float(
        string='Preço', required=True, digits='Product Price',
        readonly=False, store=True)

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)

    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            totals = line.price_unit * line.product_qty
            line.update({
                'price_subtotal': totals,
            })

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.price_unit = self.product_id.lst_price