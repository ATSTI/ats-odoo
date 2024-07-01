// console.log("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");
odoo.define('odoo_javascript.my_widget', function (require) {
	'user strict';
	
	var Widget= require('web.Widget');
	var widgetRegistry = require('web.widget_registry');
	var session = require('web.session');
	var FieldManagerMixin = require('web.FieldManagerMixin');
	// var modulo  = new Model('model_js').call('funcion_name').then(function(result){
	// 	return result;
	// });	
	// var mod = new instance.web.Model("odoo_javascript.js");
	// period= mod.call("calculate_period").then(function(result){
	// 	console.log(result);
	// }
	// );

	var MyWidget = Widget.extend(FieldManagerMixin, {
    init: function (parent, model, context) {
        this._super(parent);
        FieldManagerMixin.init.call(this);
		this._super.apply(this, arguments);	
    },

    start: function(context) {
    	var self = this;
		var nameField = this.$el.find('#name');
		// nameField.val(barcodeValue);
		// var dataset = this.dataset;
		// var active_id = dataset.ids[dataset.index];
    	this._super.apply(this, arguments);

		// console.log(id_var);

		var html ='<button id="btn_click_me" class="btn btn-primary" >Click Me</button>';
		this.$el.html(html);
		console.log("gggggggggggggggggggggggggg");
		
		this.$('#btn_click_me').click(function(context){
			// alert("I am triggered from odoo javascript.");
			session.setCompanies(1, [2]);
			console.log(context);
		});
    },

});

widgetRegistry.add(
    'my_widget', MyWidget
);

});