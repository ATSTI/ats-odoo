odoo.define("pos_partner_credit.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    const core = require("web.core");
    const _t = core._t;

    const PosRequiredCustomerPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async _isOrderValid(isForceValidate) {
                var result = super._isOrderValid(isForceValidate);
                var order = this.env.pos.get_order();
                const client = order.get_client();
                const credito = client.credit_limit_compute - client.credit
                if (this.currentOrder.is_to_invoice() && this.currentOrder.get_total_with_tax() > credito) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Sem limite de credito'),
                        body: this.env._t(
                            'Valor do pedido acima do limite disponivel. Diferença de R$' + (this.currentOrder.get_total_with_tax() - credito) + '.'
                        ),
                    });
                    return false;
                }
                return result;
            }
        };

    Registries.Component.extend(PaymentScreen, PosRequiredCustomerPaymentScreen);

    return PosRequiredCustomerPaymentScreen;
});