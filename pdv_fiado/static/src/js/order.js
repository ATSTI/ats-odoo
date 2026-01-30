odoo.define('pdv_fiado.pos_extra_note_button', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const models = require('point_of_sale.models');

    const { Order } = models;

    // =====================================================
    // Extensão do Order (estado + persistência)
    // =====================================================

    const _super_initialize = Order.prototype.initialize;
    Order.prototype.initialize = function(attributes, options) {
        _super_initialize.apply(this, arguments);
        this.extra_note = this.extra_note || '';
    };

    Order.prototype.set_extra_note = function(note) {
        this.extra_note = note ? String(note) : '';
        this.trigger('change', this); // força atualização do estado
    };  

    Order.prototype.get_extra_note = function() {
        return this.extra_note || '';
    };

    // 🔹 SALVA NO JSON DO PEDIDO
    const _super_export_json = Order.prototype.export_as_JSON;
    Order.prototype.export_as_JSON = function() {
        const json = _super_export_json.apply(this, arguments);
        json.extra_note = this.extra_note || '';
        return json;
    };

    // 🔹 RESTAURA DO JSON
    const _super_init_json = Order.prototype.init_from_JSON;
    Order.prototype.init_from_JSON = function(json) {
        _super_init_json.apply(this, arguments);
        this.extra_note = json.extra_note || '';
    };

    // 🔹 ENVIA PARA O RECIBO
    const _super_export_print = Order.prototype.export_for_printing;
    Order.prototype.export_for_printing = function() {
        const receipt = _super_export_print.apply(this, arguments);
        receipt.extra_note = this.extra_note || '';
        return receipt;
    };


    function validarCPF(cpf) {
    if (!cpf) return false;

    cpf = cpf.replace(/[^\d]+/g, '');

    if (cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false; // todos dígitos iguais

    let soma = 0;
    let resto;

    for (let i = 1; i <= 9; i++) {
        soma += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    }

    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(cpf.substring(9, 10))) return false;

    soma = 0;
    for (let i = 1; i <= 10; i++) {
        soma += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    }

    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(cpf.substring(10, 11))) return false;

    return true;
}



    const PosPaymentScreenExtra = (PaymentScreen) => class extends PaymentScreen {
        render() {
            super.render();

            const container = this.el.querySelector('.payment-controls');
            if (!container) return;

            if (!this.el.querySelector('.botaoExtra')) {
                const buttonExtra = document.createElement('div');
                buttonExtra.className = 'botaoExtra';
                buttonExtra.innerHTML = `
                    <i class="fa fa-info-circle" style="margin-right:8px;"></i>
                    Dados adicionais
                `;

                Object.assign(buttonExtra.style, {
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '75px',
                    minWidth: '150px',
                    padding: '0 12px',
                    margin: '5px',
                    backgroundColor: '#FF7F50',
                    color: '#ffffff',
                    fontWeight: 'bold',
                    fontSize: '16px',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    userSelect: 'none',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    transition: 'all 0.15s ease-in-out',
                    textAlign: 'center',
                });

                buttonExtra.addEventListener('click', async () => {
                    const order = this.currentOrder;

                    const { confirmed, payload } = await this.showPopup('TextInputPopup', {
                        title: 'CPF na nota',
                        body: 'Informe o CPF ou observações do cliente:',
                        startingValue: order.get_extra_note(),
                    });

                    if (confirmed) {
                        const valor = (payload || '').trim();
                        const somenteNumeros = valor.replace(/[^\d]+/g, '');

                        if (somenteNumeros.length === 11) {
                            if (!validarCPF(somenteNumeros)) {
                                await this.showPopup('ErrorPopup', {
                                    title: 'CPF inválido',
                                    body: 'O CPF informado não é válido. Verifique e tente novamente.',
                                });
                                return;
                            }

                            const client = order.get_client();
                            if (!client) {
                                await this.showPopup('ErrorPopup', {
                                    title: 'Cliente não selecionado',
                                    body: 'Selecione um cliente para informar CPF.',
                                });
                                return;
                            }

                            client.vat = somenteNumeros;
                            order.set_client(client);
                        }

                        order.set_extra_note(valor);
                    }


                });

                container.appendChild(buttonExtra);
            }
        }
    };

    Registries.Component.extend(PaymentScreen, PosPaymentScreenExtra);
});
