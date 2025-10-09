odoo.define('pos_receipt_custom_clube.OrderNewLineAlways', function(require) {
    'use strict';

    const models = require('point_of_sale.models');

    const _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            options = options || {};
            // Aqui não tenta achar linha igual, já cria uma nova
            const line = new models.Orderline({}, {
                pos: this.pos,
                order: this,
                product: product,
                price: options.price || product.get_price(this.pricelist, 1),
            });

            this.add_orderline(line);
            // Se quiser controlar quantidade maior que 1, adicione loop
            if (options.quantity && options.quantity > 1) {
                for (let i = 1; i < options.quantity; i++) {
                    const newLine = new models.Orderline({}, {
                        pos: this.pos,
                        order: this,
                        product: product,
                        price: options.price || product.get_price(this.pricelist, 1),
                    });
                    this.add_orderline(newLine);
                }
            }
        },
    });
});