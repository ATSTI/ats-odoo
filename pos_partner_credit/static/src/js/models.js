odoo.define("pos_partner_credit.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    models.load_fields("res.partner", ["credit"]);
    models.load_fields("res.partner", ["credit_limit_compute"]);

    models.Order = models.Order.extend({
        credito_limit: function (){
            return this.credit_limit_compute;
        }
    })
});
