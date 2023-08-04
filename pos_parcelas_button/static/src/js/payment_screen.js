/*
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define("pos_pacelas_button.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    const core = require("web.core");
    const _t = core._t;

    const PosRequiredCustomerPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async _isOrderValid(isForceValidate) {
                if (
                    this.env.pos.config.require_customer === "payment" &&
                    !this.env.pos.get_order().get_client()
                ) {
                    const result = await this.showPopup("ConfirmPopup", {
                        title: _t("An anonymous order cannot be confirmed"),
                        body: _t("Please select a customer for this order."),
                    });
                    if (result.confirmed) {
                        this.selectClient();
                    }
                    return false;
                }
                return super._isOrderValid(isForceValidate);
            }
            // _updateSelectedPaymentline() {
            //     var res = super._updateSelectedPaymentline();
            //     console.log(" executou RES : ", res)
            //     console.log(" executou EXPORT_X : ")
            //     res.ticket = '7'
            //     return res;
            // }
        };

    Registries.Component.extend(PaymentScreen, PosRequiredCustomerPaymentScreen);

    return PosRequiredCustomerPaymentScreen;
});