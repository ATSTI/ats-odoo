/** @odoo-module **/

import { registry } from "@web/core/registry";

let warningShown = false;
let reminderInterval = null;

registry.category("services").add("pending_payment_watcher", {
    dependencies: ["router", "notification", "rpc", "user"],

    start(env, { router, notification, rpc, user }) {
        const _navigate = router.pushState;

        if (_navigate) {
            router.pushState = async function (state, ...args) {

                if (!warningShown) {
                    warningShown = true;

                    const result = await rpc("/web/dataset/call_kw", {
                        model: "res.users",
                        method: "refresh_pending_payment",
                        args: [[user.userId]],
                        kwargs: {},
                    });

                    if (result) {
                        const payment_pending = result.payment_pending;
                        const overdue = result.overdue;
                        const mensage_pai = result.mensage_pai;

                        if (mensage_pai) {

                            const showNotification = () => {
                                notification.add(mensage_pai, {
                                    title: payment_pending
                                        ? "Controle Sistema"
                                        : "Aviso",
                                    type: payment_pending ? "danger" : "warning",
                                    sticky: overdue,
                                });

                                if (overdue) {
                                    setTimeout(() => {
                                        document
                                            .querySelectorAll(".o_notification_close")
                                            .forEach((btn) => btn.remove());
                                    }, 100);
                                }
                            };

                            // Mostra imediatamente
                            showNotification();

                            // Se não estiver vencido, lembra novamente a cada 1 minuto
                            if (!overdue && !reminderInterval) {
                                reminderInterval = setInterval(() => {
                                    showNotification();
                                }, 60000);
                            }
                        }
                    }
                }

                return _navigate.call(this, state, ...args);
            };
        }
    },
});