/** @odoo-module **/

import CreateOrderPopup from "point_of_sale.CreateOrderPopup";
import Registries from "point_of_sale.Registries";
import framework from "web.framework";

const {useState} = owl;

const PosDeliveryCarrierCreateOrderPopup = (CreateOrderPopup) =>
    class extends CreateOrderPopup {
        // @override
        setup() {
            super.setup();
            this.state = useState({addDeliveryCarrier: false});
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }
        onClickToShipping() {
            this.state.addDeliveryCarrier = !this.state.addDeliveryCarrier;
        }
        // @override
        async _createSaleOrder(order_state) {
            const addDeliveryCarrier = this.state.addDeliveryCarrier;
            framework.blockUI();
            const context = {
                ...this.env.session.user_context,
                add_delivery_carrier: addDeliveryCarrier,
            };
            const response = await this.rpc({
                model: "sale.order",
                method: "create_order_from_pos",
                args: [this.currentOrder.export_as_JSON(), order_state],
                kwargs: {context: context},
            })
                .catch(function (error) {
                    throw error;
                })
                .finally(function () {
                    framework.unblockUI();
                });

            if (
                addDeliveryCarrier &&
                this.env.pos.config.allow_delivery_carrier &&
                this.env.pos.config.delivery_carrier_ids
            ) {
                await this._selectDeliveryCarrierPopup(response, order_state);
            }

            // Delete current order
            this.env.pos.removeOrder(this.currentOrder);
            this.env.pos.add_new_order();

            // Close popup
            return await super.confirm();
        }
        async _selectDeliveryCarrierPopup(
            {sale_order_id, delivery_carriers},
            order_state
        ) {
            const {confirmed, payload: payload} = await this.showPopup(
                "SelectDeliveryCarrierPopup",
                {
                    carriers: delivery_carriers,
                }
            );
            const selectedCarrier = confirmed ? payload : {};
            await this._setDeliveryCarrier(sale_order_id, order_state, selectedCarrier);
            return selectedCarrier;
        }
        async _setDeliveryCarrier(sale_order_id, order_state, selectedCarrier) {
            framework.blockUI();
            const carrier_data = {};
            if (!_.isEmpty(selectedCarrier)) {
                carrier_data.carrier_id = selectedCarrier.carrier_id[0];
                carrier_data.delivery_price = selectedCarrier.delivery_price;
                carrier_data.delivery_message = selectedCarrier.delivery_message;
            }
            const response = await this.rpc({
                model: "sale.order",
                method: "action_order_from_pos",
                args: [[sale_order_id], order_state, carrier_data],
            }).catch(function (error) {
                throw error;
            }).finally(function () {
                framework.unblockUI();
            });
            return response;
        }
    };

Registries.Component.extend(CreateOrderPopup, PosDeliveryCarrierCreateOrderPopup);
