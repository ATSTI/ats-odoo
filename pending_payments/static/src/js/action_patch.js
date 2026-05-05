/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("services").add("pending_payment_watcher", {
    dependencies: ["router", "notification", "rpc", "company"],

    start(env, { router, notification, rpc, company }) {

        const _navigate = router.pushState;
        if (_navigate) {
            router.pushState = async function (state, ...args) {
                // Executa em qualquer troca de tela
                const companyId = company.currentCompany.id;
                const resultado = await rpc("/web/dataset/call_kw", {
                    model: "res.company",
                    method: "read",
                    args: [[companyId], ["payment_pending"]],
                    kwargs: {},
                });
                
                const campo = resultado?.[0]?.payment_pending;
                if (campo) {
                    notification.add("Não verificamos o seu pagamento.\n Por favor, contate o nosso financeiro.", {
                        type: "danger",
                        sticky: true,
                    });
                }

                return _navigate.call(this, state, ...args);
            };
        }
    },
});