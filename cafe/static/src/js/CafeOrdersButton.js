odoo.define('cafe.CafeOrdersButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class CafeOrdersButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        async onClick() {
            try {
                const pendingOrders = await this.rpc({
                    model: 'cafe.order',
                    method: 'get_pending_orders',
                    args: [],
                });

                if (!pendingOrders || pendingOrders.length === 0) {
                    await this.showPopup('ErrorPopup', {
                        title: 'Tidak Ada Pesanan Cafe',
                        body: 'Saat ini belum ada pesanan cafe baru yang siap dimuat.',
                    });
                    return;
                }

                const { confirmed, payload: selectedOrder } = await this.showPopup('CafeOrdersPopup', {
                    orders: pendingOrders,
                });

                if (confirmed && selectedOrder) {
                    let currentOrder = this.env.pos.get_order();

                    currentOrder.set_customer_note(`[Meja: ${selectedOrder.table_number}] - ${selectedOrder.customer_name}`);

                    for (let line of selectedOrder.lines) {
                        let productId = Array.isArray(line.product_id) ? line.product_id[0] : line.product_id;
                        let product = this.env.pos.db.get_product_by_id(productId);
                        if (product) {
                            currentOrder.add_product(product, {
                                quantity: line.quantity,
                                price: line.price_unit,
                            });
                        }
                    }

                    await this.rpc({
                        model: 'cafe.order',
                        method: 'action_set_loaded',
                        args: [[selectedOrder.id]],
                    });
                }
            } catch (error) {
                console.error('Error fetching cafe orders:', error);
                await this.showPopup('ErrorPopup', {
                    title: 'Gagal Mengambil Pesanan',
                    body: 'Terjadi kesalahan saat menghubungkan ke server.',
                });
            }
        }
    }
    CafeOrdersButton.template = 'CafeOrdersButton';

    ProductScreen.addControlButton({
        component: CafeOrdersButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(CafeOrdersButton);

    return CafeOrdersButton;
});
