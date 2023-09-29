odoo.define('button_near_create.kanban_button', function(require) {
    "use strict";
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');
    var KanbanButton = KanbanController.include({
        buttons_template: 'button_near_create.button',
        events: _.extend({}, KanbanController.prototype.events, {
            'click .open_wizard_action_kanban': '_OpenWizardKanban',
        }),
        _OpenWizardKanban: function () {
        var self = this;
         this.do_action({
            type: 'ir.actions.act_window',
            res_model: 'test.wizard',
            name :'Open Wizard',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
        });
    }
    });
    var SaleOrderKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: KanbanButton
        }),
    });
    viewRegistry.add('button_in_kanban', SaleOrderKanbanView);
 });