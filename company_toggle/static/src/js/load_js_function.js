odoo.define('company_toggle.load_js_funtion', function (require){
    "Use strict";
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var FunctionName = AbstractAction.extend({	//Add the javascript code blocks here
    });
    core.action_registry.add('js_function', FunctionName); 
    });