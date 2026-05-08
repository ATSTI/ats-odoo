odoo.define('pending_payments.action_patch', function (require) {
    'use strict';

    const WebClient = require('web.WebClient');
    const rpc = require('web.rpc');
    const session = require('web.session');
    const core = require('web.core');
    const _t = core._t;

    WebClient.include({

        show_application() {
            return this._super(...arguments).then(() => {
                return this._checkPendingPayment();
            });
        },

        _checkPendingPayment() {

            // Garante que a sessão já tem dados de empresa
            const companies = session.user_companies;


            if (!companies || !companies.current_company) {
                console.warn('[PendingPayment] session.user_companies não disponível');
                return Promise.resolve();
            }

            // No Odoo 14, current_company é [id, nome]
            const companyId = Array.isArray(companies.current_company)
                ? companies.current_company[0]
                : companies.current_company;

            return rpc.query({
                model: 'res.company',
                method: 'read',
                args: [[companyId], ['payment_pending', 'mensage_pai']],
                kwargs: {},
            }).then((result) => {

                if (result && result[0] && result[0].mensage_pai) {
                    var title = ''
                    if (result[0].payment_pending) {
                        title = 'Pagamento pendente'
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