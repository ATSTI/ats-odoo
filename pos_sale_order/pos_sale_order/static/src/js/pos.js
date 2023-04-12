odoo.define('pos_sale_order.pos_sale_orders', function (require){
"use strict"

    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');
    var Model = require('web.DataModel');
    var QWeb = core.qweb;
    var _t = core._t;


    screens.ActionpadWidget.include({
	    renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                var sale_order = {};
                var order_lines = self.pos.get_order().get_orderlines();
                sale_order.order_line = [];
                for (var line in order_lines){
                    if (order_lines[line].quantity>0)
                    {
                        var sale_order_line = [0,false,{product_id:null,product_uom_qty:0,price_unit:0.0}];
                        sale_order_line[2].product_id = order_lines[line].product.id;
                        sale_order_line[2].product_uom_qty = order_lines[line].quantity;
                        sale_order_line[2].price_unit = order_lines[line].price;
                        sale_order.order_line.push(sale_order_line);
                    }
                }
                sale_order.name = order.uid;
                if (self.pos.get_client() != null)
                {

                    sale_order.partner_id = self.pos.get_client().id;
                }
                else
                {
                    sale_order.partner_id = 81;
                }
                var saleOrderModel = new Model('sale.order');
                saleOrderModel.call('create_from_ui',[self.pos.get_order(),sale_order]).then(function(ord){
                    console.log(ord);
                });
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            self.gui.show_screen('payment');
                        },
                    });
                }else{
                    self.gui.show_screen('payment');
                }
            });
            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });
        },
	 });
});
