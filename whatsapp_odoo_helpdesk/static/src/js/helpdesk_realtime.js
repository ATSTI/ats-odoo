/** @odoo-module **/

import { busService } from "@web/core/bus/bus_service";
import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";

const { Component } = owl;

export class WhatsappHelpdeskRealtime extends Component {
    setup() {
        this.bus = useService("bus_service");
        this.action = useService("action");
        this.notification = useService("notification");

        // 🔔 Escuta mensagens no canal 'web_notify'
        useBus(this.bus, "notification", this._onNotification.bind(this));

        onMounted(() => {
            console.log("🔄 Realtime listener do WhatsApp Helpdesk ativo.");
        });
    }

    _onNotification({ channel, message }) {
        if (channel[1] !== "web_notify") return;

        try {
            const data = message.message || message;
            if (data.type === "info" && data.params && data.params.ticket_id) {
                const ticketId = data.params.ticket_id;

                // Mostra notificação visual
                this.notification.add(
                    `Nova mensagem no ticket #${ticketId}: ${data.title || ""}`,
                    { type: "info" }
                );

                // Atualiza o chatter se estiver na tela do ticket
                const current = window.location.hash || "";
                if (current.includes(`helpdesk.ticket,${ticketId}`)) {
                    console.log(`🔁 Atualizando chatter do ticket ${ticketId}...`);
                    // Força reload da view atual
                    if (current.includes(`helpdesk.ticket,${ticketId}`)) {
                        console.log(`🔁 Atualizando chatter do ticket ${ticketId}...`);

                        // Dispara um evento OWL para recarregar chatter
                        const event = new CustomEvent("reload_chatter", {
                            detail: { ticketId },
                            bubbles: true,
                        });
                        document.dispatchEvent(event);
                    }
                }
            }
        } catch (err) {
            console.error("Erro ao processar notificação realtime:", err);
        }
    }
}

registry.category("main_components").add("whatsapp_helpdesk_realtime", WhatsappHelpdeskRealtime);
