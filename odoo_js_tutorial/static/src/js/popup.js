odoo.define('odoo_js_tutorial.odoo_tutorial', function (require) {
    'use strict'

    console.log('popup.js loadedasdsa')
    var FormController = require('web.FormController');
	var session = require('web.session');
	var FieldManagerMixin = require('web.FieldManagerMixin');
    var id_empresa = 1

    var ExtendFormController = FormController.include({
        saveRecord: function () {
            // console.log('saveRecord')
            var res = this._super.apply(this, arguments);

            function parseURLParams(url) {
                var queryStart = url.indexOf("?") + 1,
                    queryEnd = url.indexOf("#") + 1 || url.length + 1,
                    query = url.slice(queryStart, queryEnd - 1),
                    pairs = query.replace(/\+/g, " ").split("&"),
                    parms = {}, i, n, v, nv;

                if (query === url || query === "") return;

                for (i = 0; i < pairs.length; i++) {
                    nv = pairs[i].split("=", 2);
                    n = decodeURIComponent(nv[0]);
                    v = decodeURIComponent(nv[1]);

                    if (!parms.hasOwnProperty(n)) parms[n] = [];
                    parms[n].push(nv.length === 2 ? v : null);
                }
                return parms;
            }


            if (this.modelName == 'odoo.tutorial') {
                // this.do_notify('Success', 'Record Saved');
                self = this;
                var url = window.location.href;
                var page_url = url.replace('#', '?');
                var params = parseURLParams(page_url);
                console.log(params)
                id_empresa = params['id'][0]
                self._rpc({
                    model: 'odoo.tutorial',
                    method: 'search_read',
                    fields: ['name', 'number_of_videos', 'company_id'],
                    domain: [['id', '=', params['id'][0]]],
                    context: self.context,
                }).then(function (result) {
                    console.log(result)
                    if (result[0]['number_of_videos'] == 0) {
                        self.do_notify('Warning', 'Number of videos is 0');
                    }
                })
            }

            return res;

        }
    });
    
    var button = Button.extend(FieldManagerMixin, {
        init: function Mbutton (parent, model, context) {
            this._super(parent);
            FieldManagerMixin.init.call(this);
            this._super.apply(this, arguments);	
        },
    
        start: function Mbutton (context) {
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
                session.setCompanies(id_empresa, id_empresa);
                console.log(context);
            });
        }
    })
});