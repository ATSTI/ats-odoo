odoo.define('pending_payments.action_patch', function (require) {
    'use strict';

    // Primeira vez da sessão
    if (!sessionStorage.getItem('pending_assets_reload')) {

        sessionStorage.setItem('pending_assets_reload', '1');

        // Espera o Odoo terminar de montar a tela
        const wait = setInterval(() => {

            const navbar = document.querySelector('.o_main_navbar');

            if (navbar) {

                clearInterval(wait);

                console.log('RECARREGANDO O ODOO');

                // Pequeno delay extra
                setTimeout(() => {
                    window.location.reload();
                }, 300);
            }

        }, 200);
    }

    const WebClient = require('web.WebClient');
    const rpc = require('web.rpc');
    const session = require('web.session');
    const core = require('web.core');
    const _t = core._t;

    WebClient.include({

        start() {
            return this._super(...arguments).then(() => {
                return this._checkPendingPayment();
            });
        },

        _checkPendingPayment() {

            const companyId = session.user_context?.allowed_company_ids?.[0];

            if (!companyId) {
                console.warn('[PendingPayment] companyId ainda não disponível');
                return Promise.resolve();
            }

            return rpc.query({
                model: 'res.company',
                method: 'read',
                args: [[companyId], ['payment_pending', 'mensage_pai']],
                kwargs: {},
            }).then((result) => {

                if (result && result[0] && result[0].mensage_pai) {
                    var title = ''
                    if (result[0].payment_pending) {
                        title = 'Controle Sistema'
                    }
                    else {
                        title = 'Aviso'
                    }
                    // Agenda para depois do render
                    setTimeout(() => {
                        this.displayNotification({
                            title: title,
                            message: result[0].mensage_pai,
                            type: 'warning',
                            sticky: true,
                        });

                        setTimeout(() => {
                            $('.close.o_notification_close').remove();
                        }, 100);
                    }, 1000);

                } else {
                    console.log('[PendingPayment] payment_pending = FALSE');
                }

            }).catch((err) => {

                console.error('[PendingPayment] erro no rpc:', err);

            });
        },
    });

});