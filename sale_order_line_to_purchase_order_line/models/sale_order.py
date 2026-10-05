# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vendor_id = fields.Many2one(
        'res.partner', string="Vendor",
        help="Fornecedor usado apenas para produtos SEM fornecedor "
             "cadastrado no produto.")
    purchase_id = fields.Many2one(
        'purchase.order', string="Purchase Order",
        domain=[('state', '=', 'draft')],
        help="Se preenchido, todas as linhas selecionadas são adicionadas "
             "a este pedido de compra existente (sem separar por fornecedor).")
    purchase_order_ids = fields.Many2many(
        'purchase.order', 'sale_order_converted_purchase_rel',
        'sale_id', 'purchase_id',
        string="Pedidos de Compra Vinculados", copy=False, readonly=True)
    purchase_count = fields.Integer(
        string="Compras", compute='_compute_purchase_count')

    @api.depends('purchase_order_ids')
    def _compute_purchase_count(self):
        for order in self:
            order.purchase_count = len(order.purchase_order_ids)

    def _get_line_seller(self, product, partner=None):
        self.ensure_one()
        today = fields.Date.context_today(self)
        sellers = product.seller_ids.filtered(
            lambda s: (not s.company_id or s.company_id == self.company_id)
            and (not s.product_id or s.product_id == product)
            and (not s.date_start or s.date_start <= today)
            and (not s.date_end or s.date_end >= today))
        if partner:
            sellers = sellers.filtered(lambda s: s.partner_id == partner)
        return sellers[:1]

    def _prepare_purchase_line_vals(self, line, purchase):
        product = line.product_id
        uom_po = product.uom_po_id or line.product_uom
        qty = line.product_uom._compute_quantity(
            line.product_uom_qty, uom_po)
        seller = self._get_line_seller(product, purchase.partner_id)
        price = seller.price if seller and seller.price else 0.0
        return {
            'product_id': product.id,
            'name': line.name,
            'product_qty': qty,
            'product_uom': uom_po.id,
            'price_unit': price,
            'order_id': purchase.id,
            'taxes_id': [(6, 0, line.tax_id.ids)],
        }

    def _create_purchase_line(self, line, purchase):
        vals = self._prepare_purchase_line_vals(line, purchase)
        po_line = self.env['purchase.order.line'].create(vals)
        po_line.write({
            'product_qty': vals['product_qty'],
            'price_unit': vals['price_unit'],
        })
        return po_line

    def action_convert_po(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda l: l.is_check and l.product_id and not l.display_type)
        if not lines:
            raise ValidationError(_("Select Order Line"))

        PurchaseOrder = self.env['purchase.order']
        purchases = PurchaseOrder
        created = PurchaseOrder

        if self.purchase_id:
            purchases = self.purchase_id
            for line in lines:
                self._create_purchase_line(line, self.purchase_id)
        else:
            grouped = {}
            sem_fornecedor = []
            for line in lines:
                vendor = self._get_line_seller(line.product_id).partner_id
                if not vendor:
                    vendor = self.vendor_id
                if not vendor:
                    sem_fornecedor.append(line.product_id.display_name)
                    continue
                grouped.setdefault(vendor, self.env['sale.order.line'])
                grouped[vendor] |= line

            if sem_fornecedor:
                raise ValidationError(_(
                    "Os produtos abaixo não possuem fornecedor cadastrado "
                    "e nenhum Vendor foi selecionado:\n- %s",
                    "\n- ".join(sem_fornecedor)))

            for vendor, vendor_lines in grouped.items():
                purchase = PurchaseOrder.create({
                    'partner_id': vendor.id,
                    'origin': self.name,
                    'company_id': self.company_id.id,
                })
                for line in vendor_lines:
                    self._create_purchase_line(line, purchase)
                purchases |= purchase
            created = purchases

        self.purchase_order_ids = [(4, po.id) for po in purchases]

        action = self.env.ref('purchase.action_rfq_form')
        if created:
            title_msg = _('Novos pedidos de compra criados: ')
        else:
            title_msg = _('Linhas adicionadas ao pedido de compra: ')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': title_msg + ', '.join(['%s'] * len(purchases)),
                'links': [{
                    'label': po.name,
                    'url': f'#action={action.id}&id={po.id}'
                           f'&model=purchase.order',
                } for po in purchases],
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id(
            'purchase.purchase_rfq')
        pos = self.purchase_order_ids
        if len(pos) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id,
                                'form')]
            action['res_id'] = pos.id
        else:
            action['domain'] = [('id', 'in', pos.ids)]
        return action


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_check = fields.Boolean(
        string="Select", help="Marque para converter a linha em compra.")