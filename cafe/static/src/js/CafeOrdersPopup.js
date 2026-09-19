odoo.define('cafe.CafeOrdersPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useState } = owl.hooks;

    class CafeOrdersPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({
                selectedOrder: null,
            });
        }

        selectOrder(order) {
            this.state.selectedOrder = order;
        }

        getPayload() {
            return this.state.selectedOrder;
        }
    }

    CafeOrdersPopup.template = 'CafeOrdersPopup';
    CafeOrdersPopup.defaultProps = {
        confirmText: 'Muat ke Keranjang',
        cancelText: 'Batal',
        title: 'Pesanan Cafe Pending',
        orders: [],
    };

    Registries.Component.add(CafeOrdersPopup);

    return CafeOrdersPopup;
});
