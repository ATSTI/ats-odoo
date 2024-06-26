odoo.define('odoo_javascript.js', function (require) {
    "use strict";
    
    var rpc = require('web.rpc');
    
    $(document).on('click', '#test_button', function () {
    
    console.log("test")
    return rpc.query({
            model: 'odoo_javascript.js',
            method: 'get_sale_order',
            args: [""],
        }).then(function (result) {
            console.log(result);
        });
    });
});
    
