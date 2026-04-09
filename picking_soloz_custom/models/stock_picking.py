from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        # ('separacao', 'Separação'),
        ('conferencia', 'Conferência'),
        ('done', 'Done'),                # ← só para concluído de verdade
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
        tracking=True,
    )

    state_locked = fields.Boolean(default=False, copy=False)

#     separador_id = fields.Many2one('res.users', string='Separador', tracking=True)
#     conferente_id = fields.Many2one('res.users', string='Conferente', tracking=True)
#     # separador_domain = fields.Json(compute='_compute_user_domains')
#     # conferente_domain = fields.Json(compute='_compute_user_domains')
#     is_conferente = fields.Boolean(compute='_compute_is_conferente')
#     conferencia_validada = fields.Boolean(string='Conferência Validada', default=False, copy=False)
#     divergencia_count = fields.Integer(string="Divergências", compute="_compute_divergencias")

#     # ─── COMPUTES ────────────────────────────────────────────────────────────────

#     @api.depends('conferente_id')
#     def _compute_is_conferente(self):
#         for rec in self:
#             rec.is_conferente = rec.conferente_id.id == self.env.uid

#     @api.depends("move_ids_without_package.diferenca")
#     def _compute_divergencias(self):
#         for picking in self:
#             picking.divergencia_count = len(
#                 picking.move_ids_without_package.filtered(lambda m: m.diferenca != 0)
#             )

#     @api.depends(
#         'move_type',
#         'immediate_transfer',
#         'move_ids.state',
#         'move_ids.conferencia',
#     )
#     def _compute_state(self):
#         # Estados customizados que não devem ser sobrescritos pelo compute nativo
#         estados_locked = ('separacao', 'conferencia', 'transito', 'entregue')

#         # Separa pickings com estado travado dos demais
#         locked = self.filtered(lambda p: p.state_locked and p.state in estados_locked)
#         normal = self - locked

#         # Roda o compute nativo apenas nos pickings sem estado travado
#         if normal:
#             super(Picking, normal)._compute_state()

#         # Para os lockados, mantém o estado atual
#         for picking in locked:
#             picking.state = picking.state

#     # ─── ACTIONS ─────────────────────────────────────────────────────────────────

#     def action_assign(self):
#         """Verifica disponibilidade e muda para reservado após reserva completa."""
#         self.filtered(lambda p: p.state == 'draft').action_confirm()
#         moves = self.move_ids.filtered(
#             lambda m: m.state not in ('draft', 'cancel', 'done')
#         ).sorted(
#             key=lambda m: (-int(m.priority), not bool(m.date_deadline), m.date_deadline, m.date, m.id)
#         )
#         if not moves:
#             raise UserError(_('Nothing to check the availability for.'))
#         moves._action_assign()

#         for picking in self:
#             moves_ativos = picking.move_ids.filtered(lambda m: m.state not in ('cancel', 'done'))
#             if moves_ativos and all(m.state == 'assigned' for m in moves_ativos):
#                 picking.write({'state': 'assigned', 'state_locked': True})

#         return True

#     def action_marcar_separacao(self):
#         self.ensure_one()

#         if not self.separador_id:
#             raise UserError(_("É necessário definir um Separador antes de iniciar a separação."))

#         if not self.conferente_id:
#             raise UserError(_("É necessário definir um Conferente antes de iniciar a Conferência."))

#         moves = self.move_ids_without_package.filtered(lambda m: m.state not in ('done', 'cancel'))
#         nao_reservados = moves.filtered(lambda m: m.state != 'assigned')

#         if nao_reservados:
#             produtos = ', '.join(nao_reservados.mapped('product_id.display_name'))
#             raise UserError(_(
#                 "Os seguintes produtos não estão totalmente reservados:\n%s"
#             ) % produtos)

#         self.write({'state': 'separacao', 'state_locked': True})
    
    def action_agrupar_linhas(self):
        for picking in self:
            agrupados = {}
            for move in picking.move_ids_without_package.filtered(lambda m: m.state not in ['done', 'cancel']):
                key = (move.product_id.id, move.sale_line_id.id)

                if key not in agrupados:
                    agrupados[key] = move
                else:
                    principal = agrupados[key]
                    principal.product_uom_qty += move.product_uom_qty
                    move.unlink()
        return True

#     def action_separar_todos_e_conferir(self):
#         self.ensure_one()
#         if self.env.user != self.separador_id:
#             raise UserError(_("Apenas o usuário definido como Separador pode iniciar a separação."))
#         moves = self.move_ids_without_package.filtered(lambda m: m.state not in ('done', 'cancel'))
#         moves.write({'separacao': True})
#         self.write({'state': 'conferencia', 'state_locked': True})

#     def action_validar_conferencia(self):
#         self.ensure_one()
#         if self.env.user != self.conferente_id:
#             raise UserError(_("Apenas o usuário definido como Conferente pode iniciar a conferência."))
#         moves = self.move_ids_without_package.filtered(lambda m: m.state not in ('done', 'cancel'))
#         divergentes = moves.filtered(lambda m: m.conferencia != m.product_uom_qty)

#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Resultado da Conferência',
#             'res_model': 'wizard.validar.conferencia',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {
#                 'default_picking_id': self.id,
#                 'default_tem_divergencia': bool(divergentes),
#                 'default_line_ids': [(0, 0, {
#                     'product_id': m.product_id.id,
#                     'qty_conferida': m.conferencia,
#                 }) for m in divergentes],
#             }
#         }

    def action_transito(self):
        for picking in self:
            picking.write({'state': 'transito', 'state_locked': True})

    def action_entregue(self):
        for picking in self:
            picking.write({'state': 'entregue', 'state_locked': True})

#     def action_aguardando(self):
#         for picking in self:
#             picking.write({'state': 'confirmed', 'state_locked': False})

#     def action_concluido(self):
#         for picking in self:
#             picking.write({'state': 'done', 'state_locked': True})
    
#     def action_pronto(self):
#         for picking in self:
#             picking.write({'state': 'assigned', 'state_locked': True})

#     def action_reload(self):
#         return

#     # ─── WRITE ───────────────────────────────────────────────────────────────────

#     def write(self, vals):
#         gerente = self.env.user.has_group('stock.group_stock_manager')
#         campos_restritos = {'separador_id', 'conferente_id'}

#         if campos_restritos.intersection(vals) and not gerente:
#             raise UserError(_("Apenas o Administrador de Inventário pode atribuir Separador e Conferente."))

#         return super().write(vals)

#     # ─── ACTION UPDATE STOCK ──────────────────────────────────────────────────────

#     def action_update_stock(self):
#         self.ensure_one()
#         sale_order = self.move_ids.mapped("sale_line_id.order_id")[:1]
#         if not sale_order and self.origin:
#             sale_order = self.env["sale.order"].search([("name", "=", self.origin)], limit=1)
#         if not sale_order:
#             return

#         Move = self.env["stock.move"]
#         bom_products = {}
#         for line in sale_order.order_line:
#             product = line.product_id
#             bom_dict = self.env["mrp.bom"]._bom_find(products=product)
#             bom = bom_dict.get(product)
#             if not bom:
#                 continue
#             for bom_line in bom.bom_line_ids:
#                 pid = bom_line.product_id.id
#                 qty = bom_line.product_qty * line.product_uom_qty
#                 if pid not in bom_products:
#                     bom_products[pid] = {"qty": 0, "uom": bom_line.product_uom_id.id}
#                 bom_products[pid]["qty"] += qty

#         if not bom_products:
#             return

#         picking_moves = {}
#         for m in self.move_ids.filtered(lambda m: m.state not in ("done", "cancel")):
#             picking_moves.setdefault(m.product_id.id, []).append(m)

#         for product_id, data in bom_products.items():
#             moves = picking_moves.get(product_id)
#             if moves:
#                 for move in moves:
#                     if move.product_uom_qty != data["qty"]:
#                         move.write({"product_uom_qty": data["qty"]})
#             else:
#                 Move.create({
#                     "name": self.env["product.product"].browse(product_id).display_name,
#                     "product_id": product_id,
#                     "product_uom_qty": data["qty"],
#                     "product_uom": data["uom"],
#                     "picking_id": self.id,
#                     "location_id": self.location_id.id,
#                     "location_dest_id": self.location_dest_id.id,
#                 })

#         for product_id, moves in picking_moves.items():
#             if product_id not in bom_products:
#                 for move in moves:
#                     move._do_unreserve()
#                     move._action_cancel()
#                     move.unlink()


# class StockMove(models.Model):
#     _inherit = "stock.move"

#     separacao = fields.Boolean(string="Separação")
#     conferencia = fields.Float(string="Conferência")
#     diferenca = fields.Float(string="Diferença", compute="_compute_diferenca", store=True)
#     concluido = fields.Boolean(string="Concluído", compute="_compute_concluido", store=True)
#     todos_separados = fields.Boolean(
#         string="Todos Separados",
#         compute="_compute_todos_separados",
#         store=False,
#     )

#     @api.depends("picking_id.move_ids_without_package.separacao")
#     def _compute_todos_separados(self):
#         for move in self:
#             if not move.picking_id:
#                 move.todos_separados = False
#                 continue
#             moves = move.picking_id.move_ids_without_package.filtered(
#                 lambda m: m.state not in ("done", "cancel")
#             )
#             move.todos_separados = bool(moves) and all(m.separacao for m in moves)

#     @api.depends("conferencia", "product_uom_qty")
#     def _compute_diferenca(self):
#         for move in self:
#             move.diferenca = move.conferencia - move.product_uom_qty

#     @api.depends("conferencia", "product_uom_qty")
#     def _compute_concluido(self):
#         for move in self:
#             move.concluido = move.conferencia == move.product_uom_qty