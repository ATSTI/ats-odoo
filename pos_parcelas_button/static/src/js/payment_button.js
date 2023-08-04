// ISSO FUNCIONA
// odoo.define("pos_membership.PaymentScreen", function (require) {
//     "use strict";

//     const PaymentScreen = require("point_of_sale.PaymentScreen");
//     const Registries = require("point_of_sale.Registries");

//     // eslint-disable-next-line no-shadow
//     const OverloadPaymentScreen = (PaymentScreen) =>
//         // eslint-disable-next-line no-shadow
//         class OverloadPaymentScreen extends PaymentScreen {
//             async _isOrderValid() {
//                 var op = document.getElementById('inlinesOptions').value;
//                 console.log(" OBJETO THIS : ", this)
//                 console.log(" Ticket Original : ", this.ticket)
//                 this.ticket = op
//                 console.log(" Ticket NOVO : ", this.ticket)
//                 // var newPaymentline = new exports.Paymentline({},{order: this, payment_method:payment_method, pos: this.pos});
//                 return await super._isOrderValid(...arguments);
//             }
//         };

//     Registries.Component.extend(PaymentScreen, OverloadPaymentScreen);

//     return PaymentScreen;
// });



odoo.define("pos_parcelas_button.models", function (require) {
    "use strict";

    // const models = require("point_of_sale.models");

    var op = document.getElementById('inlinesOptions').value;
    // console.log(" OBJETO THIS : ", this)
    console.log("sXXXXXXXXXXXXXXXXX")

    var PayParc = require("point_of_sale.PaymentLine")
    var Pay = PayParc.extend({
        export_as_JSON: function () {
            // const exp_json = order_super.export_as_JSON.apply(this, arguments);
            console.log(" ENTROU OVERRIDE ")
            this.export_x();
            console.log(" executou EXPORT_X : ", op)
            // console.log(" OBJ This : ", this)
            // console.log(" OBJ Line : ", exp_json)
            // debugger;
        },
        export_x: function () {
            return {
                name: time.datetime_to_str(new Date()),
                payment_method_id: this.payment_method.id,
                amount: this.get_amount(),
                payment_status: this.payment_status,
                can_be_reversed: this.can_be_resersed,
                ticket: op,
                card_type: this.card_type,
                cardholder_name: this.cardholder_name,
                transaction_id: this.transaction_id,
            };
        }
    })

    var pay = new Pay();
    pay.export_as_JSON()


    // PayParc.include({
    //     render: function () {
    //         this._super();
    //     }
    // })

    // const order_super = models.Order.prototype;

    // models.Pay = models.Paymentline.extend({
    //     set_ticket: function (value) {
    //         this.ticket = value;
    //         this.trigger('change', this);
    //     },

    //     export_as_JSON: function () {
    //         const exp_json = order_super.export_as_JSON.apply(this, arguments);
    //         if (!exp_json) {
    //             return exp_json;
    //         }
    //         console.log(" ENTROU OVERRIDE ")
    //         console.log(" Ticket ZZZZZ : ", op)
    //         console.log(" OBJ This : ", this)
    //         console.log(" OBJ Line : ", exp_json)
    //         // debugger;
    //         return {
    //             name: time.datetime_to_str(new Date()),
    //             payment_method_id: this.payment_method.id,
    //             amount: this.get_amount(),
    //             payment_status: this.payment_status,
    //             can_be_reversed: this.can_be_resersed,
    //             ticket: op,
    //             card_type: this.card_type,
    //             cardholder_name: this.cardholder_name,
    //             transaction_id: this.transaction_id,
    //         };
    //     },
    // });

    // models.Order = models.Order.extend({
        // add_paymentline: function () {
        //     const line = order_super.add_paymentline.apply(this, arguments);
        //     if (!line) {
        //         return line;
        //     }
        //     // console.log(" Ticket Original : ", line.ticket)
        //     // line.ticket = op;
        //     // line.set_ticket('3');
        //     // line = {'ticket': '3'};
        //     line["ticket"] = op
        //     // console.log(" Ticket ZZZZZ : ", op)
        //     console.log(" OBJ This : ", this)
        //     console.log(" OBJ Line : ", line)
        //     return line;
        // },

    // });
});