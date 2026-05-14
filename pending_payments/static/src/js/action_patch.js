/** @odoo-module **/
import { registry } from "@web/core/registry";

let warningShown = false;

registry.category("services").add("pending_payment_watcher", {
    dependencies: ["router", "notification", "rpc", "company"],

    start(env, { router, notification, rpc, company }) {

        const _navigate = router.pushState;
        if (_navigate) {
            router.pushState = async function (state, ...args) {
                // Apenas uma vez por carregamento da página
                if (!warningShown) {
                    warningShown = true;

                    const companyId = company.currentCompany.id;

                    const resultado = await rpc("/web/dataset/call_kw", {
                        model: "res.company",
                        method: "read",
                        args: [[companyId], ["payment_pending", "mensage_pai"]],
                        kwargs: {},
                    });

                    const pendencia = resultado?.[0]?.payment_pending;
                    const msg = resultado?.[0]?.mensage_pai;
                    if (msg) {
                        warningShown = true;
                        const tipo = pendencia
                            ? "danger"
                            : "warning";
                        notification.add(msg, {
                            type: tipo,
                            sticky: true,
                        });
                        setTimeout(() => {
                            const notifications =
                                document.querySelectorAll(".o_notification");
                            const ultima =
                                notifications[notifications.length - 1];
                            ultima
                                ?.querySelector(".o_notification_close")
                                ?.remove();
                        }, 100);
                    }
                }else{
                    warningShown = false;
                }

                return _navigate.call(this, state, ...args);
            };
        }
    },
});