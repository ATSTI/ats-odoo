odoo.define('pdv_fiado.pos_fiado_button', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const PosPaymentScreenFiado = (PaymentScreen) => class extends PaymentScreen {
        render() {
            super.render();

            const container = this.el.querySelector('.payment-controls');
            if (!container) return;

            // Botão Venda a Prazo (fiado)
            if (!this.el.querySelector('.botaoFiado')) {
                const buttonFiado = document.createElement('div');
                buttonFiado.className = 'botaoFiado';
                buttonFiado.innerHTML = '<i class="fa fa-file-text-o" style="margin-right:8px;"></i> Venda a prazo';

                Object.assign(buttonFiado.style, {
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '75px',
                    minWidth: '150px',
                    padding: '0 12px',
                    margin: '5px',
                    backgroundColor: '#5A8DEE',
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

                buttonFiado.addEventListener('mouseover', () => buttonFiado.style.backgroundColor = '#4676D7');
                buttonFiado.addEventListener('mouseout', () => buttonFiado.style.backgroundColor = '#5A8DEE');

                buttonFiado.addEventListener('click', () => this.toggleIsFiado());
                container.appendChild(buttonFiado);
            }
        }

        async toggleIsFiado() {
            const order = this.currentOrder;

            if (!order.get_client()) {
                return this.showPopup('ErrorPopup', {
                    title: 'Cliente não selecionado',
                    body: 'Selecione um cliente para criar a fatura fiado.',
                });
            }

            const orderLines = order.get_orderlines().map(line => ({
                product_id: line.product.id,
                quantity: line.get_quantity(),
                price_unit: line.get_unit_price(),
                tax_ids: line.get_taxes().map(t => t.id),
            }));

            try {
                const result = await this.rpc({
                    model: 'account.move',
                    method: 'create_fiado_from_pos',
                    args: [
                        order.get_client().id,
                        orderLines,
                        order.get_total_paid()
                    ],
                });

                if (result) {
                    this.showPopup('ConfirmPopup', {
                        title: 'Fatura criada!',
                        body: `Fatura de Fiado criada com sucesso: ${result.name}`,
                    });
                    order.finalized = true;
                    this.showScreen('ReceiptScreen');
                }
            } catch (error) {
                this.showPopup('ErrorPopup', {
                    title: 'Erro ao criar Fiado',
                    body: error.message || 'Ocorreu um erro desconhecido ao criar a fatura de fiado.',
                });
            }
        }
    };

    Registries.Component.extend(PaymentScreen, PosPaymentScreenFiado);
});