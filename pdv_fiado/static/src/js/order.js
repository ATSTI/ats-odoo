odoo.define('pdv_fiado.pos_extra_note_button', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const models = require('point_of_sale.models');

    const { Order } = models;

    function limparDigitos(valor) {
        return (valor || '').replace(/\D/g, '');
    }

    function validaCPF(cpf) {
        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
        let soma = 0;
        for (let i = 0; i < 9; i++) soma += parseInt(cpf[i]) * (10 - i);
        let resto = (soma * 10) % 11;
        if (resto === 10) resto = 0;
        if (resto !== parseInt(cpf[9])) return false;

        soma = 0;
        for (let i = 0; i < 10; i++) soma += parseInt(cpf[i]) * (11 - i);
        resto = (soma * 10) % 11;
        if (resto === 10) resto = 0;
        return resto === parseInt(cpf[10]);
    }

    function validaCNPJ(cnpj) {
        if (cnpj.length !== 14 || /^(\d)\1{13}$/.test(cnpj)) return false;
        const calc = (base) => {
            let pos = base.length - 7;
            let soma = 0;
            for (let i = base.length; i >= 1; i--) {
                soma += parseInt(base[base.length - i]) * pos--;
                if (pos < 2) pos = 9;
            }
            const resultado = soma % 11;
            return resultado < 2 ? 0 : 11 - resultado;
        };
        const dv1 = calc(cnpj.substring(0, 12));
        if (dv1 !== parseInt(cnpj[12])) return false;
        const dv2 = calc(cnpj.substring(0, 13));
        return dv2 === parseInt(cnpj[13]);
    }


    const _super_initialize = Order.prototype.initialize;
    Order.prototype.initialize = function(attributes, options) {
        _super_initialize.apply(this, arguments);
        this.extra_note = this.extra_note || '';
        this.cnpj_cpf = this.cnpj_cpf || '';
    };

    Order.prototype.set_extra_note = function(note) {
        this.extra_note = note ? String(note) : '';

        const digitos = limparDigitos(this.extra_note);
        if (digitos.length === 11 && validaCPF(digitos)) {
            this.cnpj_cpf = digitos;
        } else if (digitos.length === 14 && validaCNPJ(digitos)) {
            this.cnpj_cpf = digitos;
        } else {
            this.cnpj_cpf = '';
        }

        this.trigger('change', this); 
    };

    Order.prototype.get_extra_note = function() {
        return this.extra_note || '';
    };

    Order.prototype.has_valid_cnpj_cpf = function() {
        return !!this.cnpj_cpf;
    };

    const _super_export_json = Order.prototype.export_as_JSON;
    Order.prototype.export_as_JSON = function() {
        const json = _super_export_json.apply(this, arguments);
        json.extra_note = this.extra_note || '';
        if (this.cnpj_cpf) {
            json.cnpj_cpf = this.cnpj_cpf; 
        }
        return json;
    };

    const _super_init_json = Order.prototype.init_from_JSON;
    Order.prototype.init_from_JSON = function(json) {
        _super_init_json.apply(this, arguments);
        this.extra_note = json.extra_note || '';
        this.cnpj_cpf = json.cnpj_cpf || '';
    };

    const _super_export_print = Order.prototype.export_for_printing;
    Order.prototype.export_for_printing = function() {
        const receipt = _super_export_print.apply(this, arguments);
        receipt.extra_note = this.extra_note || '';
        receipt.customer_tax_id = this.cnpj_cpf || '';
        return receipt;
    };

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
                        title: 'Dados adicionais',
                        body: 'Informe o CPF do cliente (apenas números, para constar na NFC-e):',
                        startingValue: order.get_extra_note(),
                    });

                    if (confirmed) {
                        order.set_extra_note(payload || '');

                        if (payload && !order.has_valid_cnpj_cpf()) {
                            this.showPopup('ErrorPopup', {
                                title: 'CPF/CNPJ inválido',
                                body: 'O valor informado não é um CPF ou CNPJ válido e não será enviado na NFC-e.',
                            });
                        }
                    }
                });

                container.appendChild(buttonExtra);
            }
        }
    };

    Registries.Component.extend(PaymentScreen, PosPaymentScreenExtra);
});