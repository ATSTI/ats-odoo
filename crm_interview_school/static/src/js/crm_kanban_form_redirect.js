/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { KanbanHeader } from "@web/views/kanban/kanban_header";
import { useService } from "@web/core/utils/hooks";

patch(KanbanHeader.prototype, {
    setup() {
        super.setup(...arguments);
        this.actionService = useService("action");
    },

    quickCreate() {
        if (this.group.resModel === "crm.lead") {
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "crm.lead",
                views: [[false, "form"]],
                target: "current",
                context: {
                    ...this.group.context,
                    default_stage_id: this.group.value,
                },
            });
        }
        return super.quickCreate(...arguments);
    },
});