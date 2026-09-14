# -*- coding: utf-8 -*-

import unittest
from unittest.mock import MagicMock, patch
from odoo.tests.common import TransactionCase, HttpCase


class TestCafeOrder(TransactionCase):

    def setUp(self):
        super(TestCafeOrder, self).setUp()
        self.product1 = self.env['product.product'].create({
            'name': 'Kopi Susu',
            'lst_price': 18000.0,
            'barcode': '8991001001',
            'sale_ok': True,
        })
        self.product2 = self.env['product.product'].create({
            'name': 'Roti Bakar',
            'lst_price': 15000.0,
            'barcode': '8991001002',
            'sale_ok': True,
        })

    def test_01_create_cafe_order_multi_line(self):
        order = self.env['cafe.order'].create({
            'customer_name': 'Ahmad',
            'mobile_phone': '081234567890',
            'table_number': 'T-01',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'barcode': self.product1.barcode,
                    'price_unit': self.product1.lst_price,
                    'quantity': 2,
                }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'barcode': self.product2.barcode,
                    'price_unit': self.product2.lst_price,
                    'quantity': 1,
                }),
            ]
        })
        self.assertNotEqual(order.name, 'New')
        self.assertEqual(order.amount_total, 51000.0)
        self.assertEqual(len(order.line_ids), 2)

        lines = order.line_ids
        self.assertEqual(lines[0].customer_name, 'Ahmad')
        self.assertEqual(lines[0].table_number, 'T-01')
        self.assertEqual(lines[0].barcode, '8991001001')
        self.assertEqual(lines[1].barcode, '8991002002')

    def test_02_sync_to_spreadsheet(self):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('cafe.spreadsheet_sync_active', True)
        ICP.set_param('cafe.spreadsheet_id', 'test_spreadsheet_id')

        order = self.env['cafe.order'].create({
            'customer_name': 'Siti',
            'mobile_phone': '08987654321',
            'table_number': 'T-02',
            'line_ids': [(0, 0, {
                'product_id': self.product1.id,
                'barcode': self.product1.barcode,
                'price_unit': self.product1.lst_price,
                'quantity': 1,
            })]
        })

        result = self.env['cafe.order.line'].sync_to_spreadsheet()
        self.assertIn('params', result)
