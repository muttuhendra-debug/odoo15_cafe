# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.http import request

class CafeOrderController(http.Controller):

    @http.route('/cafe/order', type='http', auth='public', website=True, csrf=True)
    def cafe_order_form(self, **post):
        if request.httprequest.method == 'POST':
            customer_name = post.get('customer_name')
            mobile_phone = post.get('mobile_phone')
            table_number = post.get('table_number')

            lines_data = post.get('lines_data')
            parsed_lines = []
            if lines_data:
                try:
                    parsed_lines = json.loads(lines_data)
                except Exception:
                    parsed_lines = []

            if customer_name and table_number and parsed_lines:
                order_lines = []
                for line in parsed_lines:
                    product_id = int(line.get('product_id'))
                    qty = float(line.get('quantity', 1.0))
                    price_unit = float(line.get('price_unit', 0.0))
                    if not price_unit:
                        prod = request.env['product.product'].sudo().browse(product_id)
                        price_unit = prod.lst_price if prod else 0.0
                    order_lines.append((0, 0, {
                        'product_id': product_id,
                        'quantity': qty,
                        'price_unit': price_unit,
                    }))

                order_vals = {
                    'customer_name': customer_name,
                    'mobile_phone': mobile_phone,
                    'table_number': table_number,
                    'line_ids': order_lines,
                }
                order = request.env['cafe.order'].sudo().create(order_vals)
                return request.render('cafe.cafe_order_success', {
                    'order': order
                })

        products = request.env['product.product'].sudo().search([('sale_ok', '=', True)])
        if not products:
            products = request.env['product.product'].sudo().search([])
        return request.render('cafe.cafe_order_form_template', {
            'products': products,
        })

    @http.route('/cafe/get_products', type='json', auth='public', website=True)
    def get_products(self):
        products = request.env['product.product'].sudo().search_read(
            [('sale_ok', '=', True)],
            ['id', 'name', 'lst_price', 'barcode']
        )
        if not products:
            products = request.env['product.product'].sudo().search_read(
                [],
                ['id', 'name', 'lst_price', 'barcode']
            )
        return products
