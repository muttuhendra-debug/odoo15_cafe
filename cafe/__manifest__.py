# -*- coding: utf-8 -*-
{
    'name': 'Cafe',
    'version': '15.0.1.0.0',
    'summary': 'Module Management Cafe',
    'sequence': 10,
    'description': """
        Module Cafe untuk Odoo 15.
        Menyediakan fitur pencatatan order cafe, detail pelanggan, meja, serta detail pesanan menu,
        serta sinkronisasi pesanan cafe dengan POS Kasir Digital.
    """,
    'category': 'Sales',
    'author': 'Jules',
    'depends': ['base', 'product', 'website', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/cafe_sequence.xml',
        'views/cafe_order_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'cafe/static/src/js/CafeOrdersButton.js',
            'cafe/static/src/js/CafeOrdersPopup.js',
            'cafe/static/src/xml/CafeOrdersButton.xml',
            'cafe/static/src/xml/CafeOrdersPopup.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
