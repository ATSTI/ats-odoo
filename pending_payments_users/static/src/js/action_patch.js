odoo.define('pending_payments_users.action_patch', function (require) {
    'use strict';

    console.log('[PendingPayment] 🔵 Módulo carregado');

    // Primeira vez da sessão
    if (!sessionStorage.getItem('pending_assets_reload')) {
        console.log('[PendingPayment] 🔄 Primeiro carregamento da sessão — agendando reload');
        sessionStorage.setItem('pending_assets_reload', '1');
        const wait = setInterval(() => {
            const navbar = document.querySelector('.o_main_navbar');
            if (navbar) {
                clearInterval(wait);
                console.log('[PendingPayment] 🟢 Navbar encontrada — recarregando em 300ms');
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

        // Hook de switch de empresa
        do_action(action, options) {
            console.log('[PendingPayment] 🔀 do_action chamado — action:', action);
            const result = this._super(...arguments);
            if (action && action.tag === 'reload_context') {
                console.log('[PendingPayment] 🏢 Switch de empresa detectado — reavaliando pendência');
                this._checkPendingPayment();
            }
            return result;
        },

        _checkPendingPayment() {
            console.log('[PendingPayment] 🔍 _checkPendingPayment() iniciado');

            const userId = session.uid;
            console.log('[PendingPayment] 👤 userId:', userId);

            if (!userId) {
                console.warn('[PendingPayment] ⚠️ userId não disponível — abortando');
                return Promise.resolve();
            }

            console.log('[PendingPayment] 📡 Chamando RPC res.users.read...');

            return rpc.query({
                model: 'res.users',
                method: 'read',
                args: [[userId], ['payment_pending', 'mensage_pai']],
                kwargs: {},
            }).then((result) => {
                console.log('[PendingPayment] 📦 Resultado RPC:', result);

                if (!result || !result[0]) {
                    console.warn('[PendingPayment] ⚠️ Resultado vazio ou inválido');
                    return;
                }

                const payment_pending = result[0].payment_pending;
                const mensage_pai = result[0].mensage_pai;

                console.log('[PendingPayment] 💳 payment_pending:', payment_pending);
                console.log('[PendingPayment] 💬 mensage_pai:', mensage_pai);

                if (mensage_pai) {
                    const title = payment_pending ? 'Controle Sistema' : 'Aviso';
                    console.log('[PendingPayment] 🔔 Exibindo notificação — title:', title, '— message:', mensage_pai);

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
                            console.log('[PendingPayment] 🗑️ Botão fechar removido');
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

    console.log('[PendingPayment] 🟢 WebClient.include() aplicado com sucesso');
});