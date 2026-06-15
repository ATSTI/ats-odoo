odoo.define('pending_payments_users.action_patch', function (require) {
    'use strict';

    // Primeira vez da sessão
    if (!sessionStorage.getItem('pending_assets_reload')) {
        console.log('[PendingPayment] 🔄 Primeiro carregamento da sessão — agendando reload');
        sessionStorage.setItem('pending_assets_reload', '1');
        const wait = setInterval(() => {
            const navbar = document.querySelector('.o_main_navbar');
            if (navbar) {
                clearInterval(wait);
                setTimeout(() => {
                    console.log('[PendingPayment] 🔁 RECARREGANDO O ODOO');
                    window.location.reload();
                }, 300);
            }
        }, 200);
    } else {
        console.log('[PendingPayment] ⏭️ Reload já feito nessa sessão — pulando');
    }

    const WebClient = require('web.WebClient');
    const rpc = require('web.rpc');
    const session = require('web.session');
    const core = require('web.core');
    const _t = core._t;

    WebClient.include({

        start() {
            console.log('[PendingPayment] 🚀 WebClient.start() chamado');
            return this._super(...arguments).then(() => {
                console.log('[PendingPayment] ✅ _super.start() concluído — chamando _checkPendingPayment');
                return this._checkPendingPayment();
            });
        },

        _checkPendingPayment() {
            console.log('[PendingPayment] 🔍 _checkPendingPayment() iniciado');

            const userId = session.uid;

            if (!userId) {
                console.warn('[PendingPayment] ⚠️ userId não disponível — abortando');
                return Promise.resolve();
            }

            return rpc.query({
                model: 'res.users',
                method: 'refresh_pending_payment',
                args: [[userId]],
            }).then((result) => {

                if (!result) {
                    console.warn('[PendingPayment] ⚠️ Resultado vazio ou inválido');
                    return;
                }

                const payment_pending = result.payment_pending;
                const mensage_pai = result.mensage_pai;

                if (mensage_pai) {
                    const title = payment_pending ? 'Controle Sistema' : 'Aviso';

                    setTimeout(() => {
                        this.displayNotification({
                            title: title,
                            message: mensage_pai,
                            type: 'warning',
                            sticky: true,
                        });
                        console.log('[PendingPayment] ✅ Notificação exibida');

                        setTimeout(() => {
                            $('.close.o_notification_close').remove();
                        }, 100);
                    }, 1000);
                } else {
                    console.log('[PendingPayment] ✅ Sem mensagem — nenhuma notificação necessária');
                }
            }).catch((err) => {
                console.error('[PendingPayment] ❌ Erro no RPC:', err);
            });
        },
    });

});