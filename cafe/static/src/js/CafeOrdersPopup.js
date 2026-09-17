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

        formatAmount(amount) {
            return 'Rp. ' + Number(amount || 0).toLocaleString('id-ID');
        }
    }
    CafeOrdersPopup.template = 'CafeOrdersPopup';
    CafeOrdersPopup.defaultProps = {
        confirmText: 'Impor ke Kasir',
        cancelText: 'Batal',
        title: 'Daftar Pesanan Cafe',
        body: '',
    };

    Registries.Component.add(CafeOrdersPopup);

    return CafeOrdersPopup;
});
