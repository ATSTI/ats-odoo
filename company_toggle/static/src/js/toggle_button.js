// console.log("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");
odoo.define('company_toggle.ToggleButton', function (require) {
    'use strict';
	
    var Widget= require('web.Widget');
	var widgetRegistry = require('web.widget_registry');
	var session = require('web.session');
	var FieldManagerMixin = require('web.FieldManagerMixin');

	var ToggleButton = Widget.extend(FieldManagerMixin, {
    init: function (parent, model, context) {
        this._super(parent);
        FieldManagerMixin.init.call(this);
		this._super.apply(this, arguments);	
    },

    start: function(context) {
    	var self = this;
		var nameField = this.$el.find('#name');
    	this._super.apply(this, arguments);

		var html ='<button id="btn_click_me" class="btn btn-primary" >TESTE</button>';
		this.$el.html(html);
		console.log("gggggggggggggggggggggggggg");
		
		this.$('#btn_click_me').click(function(context){
            session.setCompanies(1, [2]);
			console.log(context);
		});
    },

});

widgetRegistry.add(
    'toggle_button', ToggleButton
);

});
