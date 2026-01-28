odoo.define('pos_custom_button.pos_custom_button', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosPaymentScreen = (PaymentScreen) => class extends PaymentScreen {
        render() {
            super.render();

            // Evita duplicar botão
            if (!this.el.querySelector('.botaoA')) {
                const button = document.createElement('div');
                button.className = 'botaoA';
                button.innerHTML = '<i class="fa fa-file-text-o" style="margin-right:8px;"></i> Fiado';

                // Estilo inline para parecer botão nativo do POS
                    Object.assign(button.style, {
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '75px',        // mesma altura dos nativos
                        minWidth: '150px',     // largura mínima parecida
                        padding: '0 12px',
                        margin: '5px',
                        backgroundColor: '#5A8DEE', // cor padrão do POS
                        color: '#ffffff',
                        fontWeight: 'bold',
                        fontSize: '16px',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        userSelect: 'none',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                        transition: 'all 0.15s ease-in-out', // transição suave para hover e clique
                        textAlign: 'center',
                    });

                    button.addEventListener('mouseover', () => {
                        button.style.backgroundColor = '#4676D7';
                    });
                    button.addEventListener('mouseout', () => {
                        button.style.backgroundColor = '#5A8DEE';
                    });

                    button.addEventListener('mousedown', () => {
                        button.style.transform = 'translateY(2px)';
                        button.style.boxShadow = '0 1px 2px rgba(0,0,0,0.2)';
                    });
                    button.addEventListener('mouseup', () => {
                        button.style.transform = 'translateY(0)';
                        button.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
                    });
                    button.addEventListener('mouseleave', () => {
                        button.style.transform = 'translateY(0)';
                        button.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
                    });


                // Clique
                button.addEventListener('click', () => this.toggleIsFiado());

                // Adiciona no container de métodos de pagamento
                const container = this.el.querySelector('.payment-controls');
                if (container) {
                    container.appendChild(button);
                }
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

            // Prepara os produtos do pedido
            const orderLines = order.get_orderlines().map(line => ({
                product_id: line.product.id,
                quantity: line.get_quantity(),
                price_unit: line.get_unit_price(),
                tax_ids: line.get_taxes().map(t => t.id),
            }));

            try {
                // Chama o backend para criar a fatura de fiado
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

                    // Finaliza o pedido no POS
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

    Registries.Component.extend(PaymentScreen, PosPaymentScreen);
});
