odoo.define('cafe.CafeOrdersButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');

    class CafeOrdersButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        async onClick() {
            let orders = [];
            try {
                orders = await this.rpc({
                    model: 'cafe.order',
                    method: 'get_pending_orders',
                    args: [],
                });
            } catch (error) {
                console.error("Error fetching cafe orders:", error);
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Gagal Mengambil Pesanan'),
                    body: this.env._t('Terjadi kesalahan saat mengambil daftar pesanan cafe.'),
                });
                return;
            }

            const { confirmed, payload: selectedOrder } = await this.showPopup('CafeOrdersPopup', {
                title: this.env._t('Pesanan Cafe Pending'),
                orders: orders,
            });

            if (confirmed && selectedOrder) {
                await this.importOrderToCart(selectedOrder);
            }
        }

        async importOrderToCart(order) {
            try {
                const currentOrder = this.env.pos.get_order();
                if (!currentOrder) {
                    return;
                }

                for (const line of order.lines) {
                    const product = this.env.pos.db.get_product_by_id(line.product_id);
                    if (product) {
                        currentOrder.add_product(product, {
                            quantity: line.quantity,
                            price: line.price_unit,
                        });
                    } else {
                        console.warn(`Product ID ${line.product_id} (${line.product_name}) not found in POS database.`);
                    }
                }

                if (order.customer_name || order.table_number) {
                    const note = `[Cafe Order: ${order.name}] Meja: ${order.table_number || '-'} | Pemesan: ${order.customer_name || '-'}`;
                    if (typeof currentOrder.set_note === 'function') {
                        currentOrder.set_note(note);
                    }
                }

                await this.rpc({
                    model: 'cafe.order',
                    method: 'action_set_loaded',
                    args: [order.id],
                });

                await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Pesanan Berhasil Dimuat'),
                    body: this.env._t(`Pesanan ${order.name} (Meja: ${order.table_number || '-'}) telah dimasukkan ke dalam keranjang kasir.`),
                });
            } catch (error) {
                console.error("Error importing order to cart:", error);
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Gagal Memuat Pesanan'),
                    body: this.env._t('Terjadi kesalahan saat memuat pesanan ke keranjang.'),
                });
            }
        }
    }

    CafeOrdersButton.template = 'CafeOrdersButton';

    Registries.Component.add(CafeOrdersButton);

    ProductScreen.addControlButton({
        component: CafeOrdersButton,
        condition: function() {
            return true;
        },
    });

    return CafeOrdersButton;
});
