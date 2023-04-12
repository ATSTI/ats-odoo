odoo.define('pos_operation_restrict.pos_operation', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');
var QWeb = core.qweb;
var _t = core._t;

models.load_fields("res.users", ['can_give_discount','can_change_price', 'price_limit', 'discount_limit','can_delete_product']);

    /*Tentativa de incluir o pos models aqui */

    models.PosModel = models.PosModel.extend({
    delete_current_order: function(){
        //alert ('TESTE')
        if (this.get_cashier().can_delete_product){
            var order = this.get_order();
            if (order) {
                order.destroy({'reason':'abandon'});
            }
        }
        else{
           var val = 'close_order'
           this.gui.show_popup('ManagerAuthenticationPopup', {'val': val});
        }
    },

    });


	screens.OrderWidget.include({
		set_value: function(val) {
	    	var order = this.pos.get_order();
	    	if (order.get_selected_orderline()) {
	            var mode = this.numpad_state.get('mode');
	            var cashier = this.pos.get_cashier() || false;
	            if( mode === 'quantity'){
                    var vlt = val;
                    val = order.get_selected_orderline().quantity;
                    //if(val < order.get_selected_orderline().quantity){
                        //order.get_selected_orderline().set_quantity(order.get_selected_orderline().quantity);
                    //    this.gui.show_popup('ManagerAuthenticationPopup', {'val': val});
                    //}
                    if(vlt === '' || (vlt=='remove' && val > 0)){
                        //ASSIM ESTA FUNCIONANDO, MAS SE NAO COLOCAR A SENHA ELE FICA COMO REMOVE E DAI MAIS UM CLIQUE EXCLUI

                        this.gui.show_popup('ManagerAuthenticationPopup', {
                            'val': vlt,'vlt': val});
                    } else {
                        if(vlt === 'remove' && val === 0){
                            val = 'remove'
                        }    
	                    order.get_selected_orderline().set_quantity(vlt);
                    }    
	            }else if( mode === 'discount'){
	            	if(cashier && cashier.can_give_discount){
	            		if(val <= cashier.discount_limit || cashier.discount_limit < 1){
	            			order.get_selected_orderline().set_discount(val);
	            		} else {
	            			this.gui.show_popup('ManagerAuthenticationPopup', {'val': val});
	            		}
	            	} else {
	            		alert(_t('Sem permissão para dar desconto.'));
	            	}
	            }else if( mode === 'price'){
	            	if(cashier && cashier.can_change_price){
	            		order.get_selected_orderline().set_unit_price(val);
	            	} else {
	            		alert(_t('Sem permissão para alterar o preço.'));
	            	}
	            }
	    	}
	    },
	 });



	var ManagerAuthenticationPopup = PopupWidget.extend({
	    template: 'ManagerAuthenticationPopup',
	    show: function(options){
	    	var self = this;
	    	this.value = options.val || 0;
            this.valor_ant = options.vlt || 0;
	    	options = options || {};
	        this._super(options);
	        this.renderElement();
	        $('#manager_barcode').focus();
	        $('#manager_barcode').keypress(function(e){
	        	if(e.which === 13){
	        		self.click_confirm();
	        	}
	        });
	    },
	    click_confirm: function(){
	    	var self = this;
            //var valor_ant = 0;
	    	var barcode_input = $('#manager_barcode').val();
	    	if(barcode_input){
		    	if(!$.isEmptyObject(self.pos.config.pos_managers_ids)){
		    		var result_find = _.find(self.pos.users, function (o) {
		    			return o.barcode === barcode_input;
		    		});
		    		
		    		if(result_find && !$.isEmptyObject(result_find)){
		    			if($.inArray(result_find.id, self.pos.config.pos_managers_ids) != -1){
                            if(self.value > 0){
		    				 if(result_find.can_give_discount){
		    					if(self.value <= result_find.discount_limit || result_find.discount_limit < 1){
				    				self.pos.get_order().get_selected_orderline().set_discount(self.value);
				    				return this.gui.close_popup();
		    					} else {
		    						alert(_t('Desconto fora do limite permitido.'));
		    					}
		    				 } else {
		    					alert(_t(result_find.name + ' não tem desconto.'));
		    				 }
                            }
                            else if (self.value == 'close_order'){
		    				    var order = self.pos.get_order();
                                if (order) {
                                    order.destroy({'reason':'abandon'});
                                }
		    				    return this.gui.close_popup();
		    				}
                           else if((self.value === 0 || self.value== 'remove') && result_find.can_delete_product){
                                 //var line = self.value.order.selected_orderline;
                                 //self.pos.get_order().get_selected_orderline().set_quantity('remove');
                                 //self.remove_orderline(this.value);
                                 if (self.value == 'remove'){
                                    self.value = 0
                                 }
                                 self.pos.get_order().get_selected_orderline().set_quantity(self.value);
                                 return this.gui.close_popup();
                                 //self.pos.get_order().get_selected_orderline().remove_orderline(line.id);
                                 //self.pos.get_order().get_selected_orderline().numpad_state.reset();
                                 //self.pos.get_order().get_selected_orderline().update_summary();
		    				} else if(self.value == 0 || self.value== 'remove'){
                                    var valor_ant = self.pos.get_order().get_selected_orderline().quantity;
                                    self.pos.get_order().get_selected_orderline().set_quantity(valor_ant);
		    						alert(_t('Sem permissão para Excluir Item.'));
                                    return this.gui.close_popup();
		    					}
		    				else if(self.value.teste='desc_button'){
		    				    this.gui.close_popup();
		    				    return this.gui.show_popup('number',{
                                    'title': _t('Discount Percentage'),
                                    'value': this.pos.config.discount_pc,
                                    'confirm': function(val) {
                                        val = Math.round(Math.max(0,Math.min(100,val)));
                                        self.value.apply_discount(val);
                                    },
                                });
		    				}


                            //if(self.value === ' ' && result_find.can_delete_product){
                                 //var line = self.value.order.selected_orderline;
                                 //self.pos.get_order().get_selected_orderline().set_quantity('remove');
                                 //self.remove_orderline(this.value);
                            //     self.pos.get_order().order.get_selected_orderline().set_quantity(val);
                            //     this.gui.close_popup();
                                 //self.pos.get_order().get_selected_orderline().remove_orderline(line.id);
                                 //self.pos.get_order().get_selected_orderline().numpad_state.reset();
                                 //self.pos.get_order().get_selected_orderline().update_summary();
		    				//	} else {
		    				//		alert(_t('Sem permissão para Excluir Item.'));
		    				//	}
                            
		    			} else {
		    				alert(_t('Não é gerente.'));
			    		}
		    		} else {
		    			alert(_t('Senha Invalida'));
		    			$('#manager_barcode').val('');
		    			$('#manager_barcode').focus();
		    		}
	    	}else{
	    		alert(_t('Por favor, digite sua senha.'));
	    		$('#manager_barcode').focus();
	    	}
          }  
	    },
	});
	gui.define_popup({name:'ManagerAuthenticationPopup', widget: ManagerAuthenticationPopup});

});
