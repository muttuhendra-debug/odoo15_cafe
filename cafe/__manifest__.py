# -*- coding: utf-8 -*-
{
    'name': 'Cafe',
    'version': '15.0.1.0.0',
    'summary': 'Module Management Cafe',
    'sequence': 10,
    'description': """
        Module Cafe untuk Odoo 15.
        Menyediakan fitur pencatatan order cafe, detail pelanggan, meja, detail pesanan menu,
        serta sinkronisasi ke Google Spreadsheet dan Mobile-Responsive Order Form.
    """,
    'category': 'Sales',
    'author': 'Jules',
    'depends': ['base', 'product', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/cafe_sequence.xml',
        'data/cafe_cron.xml',
        'views/cafe_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/cafe_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
