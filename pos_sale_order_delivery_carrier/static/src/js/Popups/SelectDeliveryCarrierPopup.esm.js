/** @odoo-module **/

import AbstractAwaitablePopup from "point_of_sale.AbstractAwaitablePopup";
import Registries from "point_of_sale.Registries";
import {_lt} from "@web/core/l10n/translation";

const {useState} = owl;

class SelectDeliveryCarrierPopup extends AbstractAwaitablePopup {
    setup() {
        super.setup();
        this.state = useState({selectedCarrier: this.props.carriers[0]});
    }
    onChange(selectedCarrierId) {
        const selected = this.props.carriers.find(
            (item) => parseInt(selectedCarrierId) === item.carrier_id[0]
        );
        this.state.selectedCarrier = selected;
    }
    getPayload() {
        return this.props.carriers.find((item) => this.state.selectedCarrier === item);
    }
}

SelectDeliveryCarrierPopup.template = "SelectDeliveryCarrierPopup";
SelectDeliveryCarrierPopup.defaultProps = {
    confirmText: _lt("Confirm"),
    cancelText: _lt("Cancel"),
    title: _lt("Add a shipping method"),
    body: "",
    list: [],
    confirmKey: false,
};

Registries.Component.add(SelectDeliveryCarrierPopup);

export default SelectDeliveryCarrierPopup;
