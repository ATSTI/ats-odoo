/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Chatter } from "@mail/chatter/web_portal/chatter"; // caminho válido no Odoo 18

patch(Chatter.prototype, "whatsapp_chatter_reload", {
    setup() {
        this._super(...arguments);

        // Escuta evento global que vem do nosso módulo realtime
        document.addEventListener("reload_chatter", async (ev) => {
            const { ticketId } = ev.detail || {};
            const record = this.props.record;

            // Verifica se o chatter atual é do ticket que recebeu atualização
            if (
                record &&
                record.resModel === "helpdesk.ticket" &&
                record.resId === ticketId
            ) {
                console.log(`🔁 Recarregando chatter do ticket #${ticketId}`);
                try {
                    await this.model.loadNewMessages();
                    this.render(); // força rerender se necessário
                } catch (error) {
                    console.error("Erro ao atualizar chatter:", error);
                }
            }
        });
    },
});
