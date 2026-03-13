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
    
    def action_aguardando(self):
        for picking in self:
            picking.write({'state': 'confirmed'})
    
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
        # import pudb;pudb.set_trace()
        sale_order = self.move_ids.mapped("sale_line_id.order_id")[:1]
        if not sale_order and self.origin:
            sale_order = self.env["sale.order"].search([("name", "=", self.origin)], limit=1)
        if not sale_order:
            return

        Move = self.env["stock.move"]
        bom_products = {}
        for line in sale_order.order_line:
            product = line.product_id
            bom_dict = self.env["mrp.bom"]._bom_find(products=product)
            bom = bom_dict.get(product)
            if not bom:
                continue
            for bom_line in bom.bom_line_ids:
                pid = bom_line.product_id.id
                qty = bom_line.product_qty * line.product_uom_qty
                if pid not in bom_products:
                    bom_products[pid] = {
                        "qty": 0,
                        "uom": bom_line.product_uom_id.id,
                    }
                bom_products[pid]["qty"] += qty
        if not bom_products:
            return
        picking_moves = {}
        for m in self.move_ids.filtered(lambda m: m.state not in ("done", "cancel")):
            picking_moves.setdefault(m.product_id.id, []).append(m)
        for product_id, data in bom_products.items():
            moves = picking_moves.get(product_id)
            if moves:
                for move in moves:
                    if move.product_uom_qty != data["qty"]:
                        move.write({
                            "product_uom_qty": data["qty"]
                        })
            else:
                Move.create({
                    "name": self.env["product.product"].browse(product_id).display_name,
                    "product_id": product_id,
                    "product_uom_qty": data["qty"],
                    "product_uom": data["uom"],
                    "picking_id": self.id,
                    "location_id": self.location_id.id,
                    "location_dest_id": self.location_dest_id.id,
                })

        for product_id, moves in picking_moves.items():
            if product_id not in bom_products:
                for move in moves:
                    move._do_unreserve()
                    move._action_cancel()
                    move.unlink()

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