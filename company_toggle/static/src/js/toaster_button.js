odoo.define('company_toggle.ToasterButton', function (require) {
    'use strict';

    const widgetRegistry = require('web.widget_registry');
    const Widget = require('web.Widget');
    var FieldManagerMixin = require('web.FieldManagerMixin');

    const ToasterButton = Widget.extend(FieldManagerMixin, {
        template: 'purchase.ToasterButton',
        xmlDependencies: ['/company_toggle/static/src/xml/toaster_button.xml'],
        events: Object.assign({}, Widget.prototype.events, {
            'click': '_onClickButton',
        }),

        init: function (parent, data, node) {
            this._super(parent);
            this.button_name = node.attrs.button_name;
            this.title = node.attrs.title;
            this.id = data.res_id;
            this.model = data.model;
            FieldManagerMixin.init.call(this);
            this._super.apply(this, arguments);	
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        _onClickButton: function (ev) {
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

    widgetRegistry.add('toaster_button', ToasterButton);

    return ToasterButton;
});