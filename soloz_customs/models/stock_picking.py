from odoo import models, fields, api

class Picking(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('separacao', 'Separação'),
        ('conferencia', 'Conferência'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('transito', 'Em trânsito'),
        ('entregue', 'Entregue'),
        ('cancel', 'Cancelled'),
    ],
        string="Status",
        compute="_compute_state",
        copy=False,
        index=True,
        readonly=True,
        store=True,
        tracking=True
    )

    divergencia_count = fields.Integer(
        string="Divergências",
        compute="_compute_divergencias"
    )
    def action_transito(self):
        for picking in self:
            picking.write({'state': 'transito'})

    def action_entregue(self):
        for picking in self:
            picking.write({'state': 'entregue'})
    
    def action_reload(self):
        return 

    @api.depends("move_ids_without_package.diferenca")
    def _compute_divergencias(self):
        for picking in self:
            picking.divergencia_count = len(
                picking.move_ids_without_package.filtered(lambda m: m.diferenca != 0)
            )
    @api.depends(
        'move_type',
        'immediate_transfer',
        'move_ids.state',
        'move_ids.separacao',
        'move_ids.conferencia',
    )
    def _compute_state(self):
        super()._compute_state()
        for picking in self:
            moves = picking.move_ids_without_package.filtered(lambda m: m.state not in ('done', 'cancel'))
            if not moves:
                continue
            if any(m.separacao for m in moves) and picking.state not in ('conferencia', 'assigned', 'done'):
                picking.state = 'separacao'
            if picking.state in ('confirmed', 'separacao', 'assigned'):
                if all(m.separacao for m in moves):
                    picking.state = 'conferencia'
            if picking.state == 'conferencia':
                if all(m.conferencia == m.product_uom_qty for m in moves):
                    picking.state = 'assigned'

    def action_update_stock(self):
        self.ensure_one()
        sale_order = self.sale_id
        if not sale_order:
            return

        for line in sale_order.order_line:
            product = line.product_id
            bom_dict = self.env['mrp.bom']._bom_find(products=product)
            bom = bom_dict.get(product)
            if not bom:
                continue

            bom_lines, _ = bom.explode(product, line.product_uom_qty)
            for bom_line, line_data in bom_lines:
                if bom_line._name != 'mrp.bom.line':
                    continue

                existing_move = self.move_ids.filtered(
                    lambda m: m.product_id == bom_line.product_id and m.state not in ('done', 'cancel')
                )

                if existing_move:
                    existing_move[0].write({
                        'product_uom_qty': line_data['qty'],
                        'product_uom': bom_line.product_uom.id,
                    })
                else:
                    self.env['stock.move'].create({
                        'name': bom_line.product_id.name,
                        'product_id': bom_line.product_id.id,
                        'product_uom_qty': line_data['qty'],
                        'product_uom': bom_line.product_uom.id,
                        'picking_id': self.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                    })

        self.move_ids._action_assign()


class StockMove(models.Model):
    _inherit = "stock.move"

    separacao = fields.Boolean(string="Separação")
    conferencia = fields.Float(string="Conferência")
    diferenca = fields.Float(string="Diferença", compute="_compute_diferenca", store=True)
    concluido = fields.Boolean(string="Concluído", compute="_compute_concluido", store=True)

    todos_separados = fields.Boolean(
    string="Todos Separados",
    compute="_compute_todos_separados",
    store=False,
)

    @api.depends("picking_id.move_ids_without_package.separacao")
    def _compute_todos_separados(self):
        for move in self:
            if not move.picking_id:
                move.todos_separados = False
                continue
            moves = move.picking_id.move_ids_without_package.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            move.todos_separados = bool(moves) and all(m.separacao for m in moves)
    @api.depends("conferencia", "product_uom_qty")
    def _compute_diferenca(self):
        for move in self:
            move.diferenca = move.conferencia - move.product_uom_qty

    @api.depends("conferencia", "product_uom_qty")
    def _compute_concluido(self):
        for move in self:
            move.concluido = move.conferencia == move.product_uom_qty

    # def write(self, vals):
    #     res = super().write(vals)
    #     if 'separacao' in vals:
    #         pickings = self.mapped('picking_id')
    #         should_reload = False

    #         for picking in pickings:
    #             moves_ativos = picking.move_ids_without_package.filtered(
    #                 lambda m: m.state not in ('done', 'cancel')
    #             )
    #             if any(m.separacao for m in moves_ativos) and picking.state not in ('conferencia', 'assigned', 'done'):
    #                 picking.write({'state': 'separacao'})
    #             if moves_ativos and all(m.separacao for m in moves_ativos):
    #                 picking.write({'state': 'conferencia'})
    #                 should_reload = True  # ← flag when all are separated
    

    #         if should_reload:
    #             return {
    #                 "type": "ir.actions.client",
    #                 "tag": "reload",
    #             }

    #     if 'conferencia' in vals:
    #         for move in self:
    #             move.concluido = move.conferencia == move.product_uom_qty
    #         pickings = self.mapped('picking_id')
    #         for picking in pickings:
    #             moves_nao_cancelados = picking.move_ids_without_package.filtered(
    #                 lambda m: m.state not in ('done', 'cancel')
    #             )
    #             if moves_nao_cancelados and all(m.concluido for m in moves_nao_cancelados):
    #                 picking.write({'state': 'assigned'})

    #     return res