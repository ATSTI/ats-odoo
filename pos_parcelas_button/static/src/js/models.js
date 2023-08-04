/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).*/
odoo.define("pos_pacelas_button.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    // const order_super = models.PaymentLine.prototype;
    // var pay_super = models.PaymentLine.prototype;
    // var op = document.getElementById('inlinesOptions').value;
    // console.log(" executou EXPORT_X : ", op)
    // var _paymentlineproto = models.Paymentline.prototype;
    // models.Paymentline = models.Paymentline.extend({
    //     initialize: function () {
    //         var res = _paymentlineproto.initialize.apply(this, arguments);
    //         if (this.payment_method.id === 2){
    //             abrir();
    //         }
    //         return res;
    //     },
    // });
    // models.load_fields('pos.order', ['parcela']);    //Add the customisation code
    var _paymentlineproto = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        initialize: function () {
            _paymentlineproto.initialize.apply(this, arguments);
            // Id of the terminal transaction, used to find the payment
            // line corresponding to a terminal transaction status coming
            // from the terminal driver.
            let parcela = document.getElementById('inlinesOptions');
            let existencia = document.body.contains(parcela);
            if(existencia == true){
                // if(typeof op !== null && op !== 'undefined' ) {
                console.log(" executou RRRR : ", parcela.value)
                this.ticket = parcela.value;
            }
        },
        init_from_JSON: function (json) {
            _paymentlineproto.init_from_JSON.apply(this, arguments);
            let parcela = document.getElementById('inlinesOptions');
            let existencia = document.body.contains(parcela);
            if(existencia == true){
                // if(typeof op !== null && op !== 'undefined' ) {
                console.log(" executou SSSSS : ", parcela.value)
                this.ticket = parcela.value;
            }
        },
        export_as_JSON: function () {
            var vals = _paymentlineproto.export_as_JSON.apply(this, arguments);
            // var op = document.getElementById(inlinesOptions);
            let parcela = document.getElementById('inlinesOptions');
            let existencia = document.body.contains(parcela);
            if(existencia == true){
                // if(typeof op !== null && op !== 'undefined' ) {
                console.log(" executou TTTT : ", parcela.value)
                vals.ticket = parcela.value;
            }
            console.log(" PARCELA: ", vals.ticket)
            return vals;
        },
    });

});
