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
            //var default_client;
            //var client_id;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                /**if (self.pos.get_client() === null)
                {
                    client_id = parseInt('1555');
                    default_client = self.pos.db.get_partner_by_id(client_id);
                    order.set_client(default_client);
                }*/
                //if (self.pos.get_client() != null)
                if (1 === 1)
                {
                    var sale_order = {};
                    var order_lines = self.pos.get_order().get_orderlines();
                    sale_order.order_line = [];
                    for (var line in order_lines){
                        if (order_lines[line].quantity>0)
                        {
                            var sale_order_line = [0,false,{product_id:null,product_uom_qty:0}]
                            sale_order_line[2].product_id = order_lines[line].product.id;
                            sale_order_line[2].product_uom_qty = order_lines[line].quantity;
                            sale_order.order_line.push(sale_order_line);
                        }
                    }
                    sale_order.origin = 'Ponto de Venda'
                    if (self.pos.get_client() == null) {
                        sale_order.partner_id = 1555
                    }
                    else{
                        sale_order.partner_id = self.pos.get_client().id;
                    }
                    var saleOrderModel = new Model('sale.order');
                    saleOrderModel.call('create_from_ui',[self.pos.get_order(),sale_order]).then(function(ord){
                        console.log(ord)
                    })
                }
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
        }
	 });
});
