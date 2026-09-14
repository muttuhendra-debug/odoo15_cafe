# -*- coding: utf-8 -*-

import json
from odoo import http, fields, _
from odoo.http import request


class CafeWebController(http.Controller):

    @http.route(['/cafe/order'], type='http', auth='public', website=True, sitemap=True)
    def cafe_order_form(self, **kw):
        products = request.env['product.product'].sudo().search([('sale_ok', '=', True)])
        values = {
            'products': products,
            'submitted': False,
            'error': None,
            'no_footer': True,
        }
        return request.render('cafe.cafe_order_form_template', values)

    @http.route(['/cafe/order/submit'], type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def cafe_order_submit(self, **post):
        customer_name = post.get('customer_name')
        mobile_phone = post.get('mobile_phone')
        table_number = post.get('table_number')

        # Support both multi-line array input (product_id[]) and legacy single input
        product_ids = request.httprequest.form.getlist('product_id[]') or request.httprequest.form.getlist('product_id') or [post.get('product_id')]
        barcodes = request.httprequest.form.getlist('barcode[]') or request.httprequest.form.getlist('barcode') or [post.get('barcode')]
        price_units = request.httprequest.form.getlist('price_unit[]') or request.httprequest.form.getlist('price_unit') or [post.get('price_unit')]
        quantities = request.httprequest.form.getlist('quantity[]') or request.httprequest.form.getlist('quantity') or [post.get('quantity', 1)]

        # Filter out empty product selections
        valid_lines = []
        for i in range(len(product_ids)):
            p_id = product_ids[i]
            if p_id:
                bc = barcodes[i] if i < len(barcodes) else ''
                price_val = price_units[i] if i < len(price_units) else None
                qty_val = quantities[i] if i < len(quantities) else 1
                try:
                    qty = float(qty_val) if qty_val else 1.0
                except (ValueError, TypeError):
                    qty = 1.0
                try:
                    price_unit = float(price_val) if price_val is not None and price_val != '' else None
                except (ValueError, TypeError):
                    price_unit = None
                valid_lines.append((int(p_id), bc, price_unit, qty))

        if not customer_name or not table_number or not valid_lines:
            products = request.env['product.product'].sudo().search([('sale_ok', '=', True)])
            return request.render('cafe.cafe_order_form_template', {
                'products': products,
                'submitted': False,
                'error': _('Field Nama Pelanggan, Meja, dan Minimal 1 Produk wajib dipilih.')
            })

        order_line_vals = []
        Product = request.env['product.product'].sudo()
        for p_id, bc, price_unit, qty in valid_lines:
            product = Product.browse(p_id)
            if product.exists():
                unit_price = price_unit if price_unit is not None else product.lst_price
                order_line_vals.append((0, 0, {
                    'product_id': product.id,
                    'barcode': bc or product.barcode,
                    'price_unit': unit_price,
                    'quantity': qty,
                }))

        # Create Cafe Order record
        order = request.env['cafe.order'].sudo().create({
            'customer_name': customer_name,
            'mobile_phone': mobile_phone,
            'table_number': table_number,
            'line_ids': order_line_vals
        })

        products = request.env['product.product'].sudo().search([('sale_ok', '=', True)])
        return request.render('cafe.cafe_order_form_template', {
            'products': products,
            'submitted': True,
            'order': order,
            'error': None,
            'no_footer': True,
        })

    @http.route(['/cafe/get_product_barcode'], type='json', auth='public', website=True)
    def get_product_barcode(self, product_id):
        if product_id:
            product = request.env['product.product'].sudo().browse(int(product_id))
            if product.exists():
                return {'barcode': product.barcode or '', 'price': product.lst_price}
        return {'barcode': '', 'price': 0.0}
