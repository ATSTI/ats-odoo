from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_choose_delivery_fields(self):
        """
        Return name of fields to read
        """
        return [
            "carrier_id",
            "delivery_type",
            "delivery_price",
            "display_price",
            "currency_id",
            "delivery_message",
        ]

    @api.model
    def create_order_from_pos(self, order_data, action):
        config = self.env["pos.session"].browse(order_data["pos_session_id"]).config_id
        delivery_carriers = config.delivery_carrier_ids
        if not self.env.context.get("add_delivery_carrier") or not delivery_carriers:
            return super().create_order_from_pos(order_data, action)

        sale_order_line_obj = self.env["sale.order.line"]
        # create draft sale order
        order_vals = self._prepare_from_pos(order_data)
        order = self.create(order_vals)
        # create sale order lines
        for order_line_data in order_data["lines"]:
            # Create Sale order lines
            order_line_vals = sale_order_line_obj._prepare_from_pos(
                order, order_line_data[2]
            )
            sale_order_line_obj.create(order_line_vals)

        available_carriers = (
            config.delivery_carrier_ids.available_carriers(order.partner_shipping_id)
            or delivery_carriers
        )
        choose_delivery_carriers = self.env["choose.delivery.carrier"].create(
            [
                {"order_id": order.id, "carrier_id": carrier.id}
                for carrier in available_carriers
            ]
        )

        for choose in choose_delivery_carriers:
            choose._get_shipment_rate()

        return {
            "sale_order_id": order.id,
            "delivery_carriers": choose_delivery_carriers.read(
                self._get_choose_delivery_fields()
            )
            or [],
        }

    def action_order_from_pos(self, action, carrier_data):
        """
        Make action from PoS
        """
        self.ensure_one()
        if carrier_data:
            # add selected carrier before running action
            self.set_delivery_carrier_from_pos(
                carrier_data["carrier_id"],
                carrier_data["delivery_price"],
                carrier_data["delivery_message"],
            )

        # Confirm Sale Order
        if action in ["confirmed", "delivered", "invoiced"]:
            self.action_confirm()

        # mark picking as delivered
        if action in ["delivered", "invoiced"]:
            # Mark all moves are delivered
            for move in self.mapped("picking_ids.move_ids_without_package"):
                move.quantity_done = move.product_uom_qty
            self.mapped("picking_ids").button_validate()

        if action in ["invoiced"]:
            # Create and confirm invoices
            invoices = self._create_invoices()
            invoices.action_post()
        return {
            "sale_order_id": self.id,
        }

    def set_delivery_carrier_from_pos(
        self, carrier_id, delivery_price, delivery_message
    ):
        """
        Set delivery carrier from POS
        """
        self.ensure_one()
        self.set_delivery_line(
            self.env["delivery.carrier"].browse(carrier_id), delivery_price
        )
        return self.write(
            {
                "recompute_delivery_price": False,
                "delivery_message": delivery_message,
            }
        )
